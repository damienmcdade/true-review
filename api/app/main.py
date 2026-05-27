import logging
import os
import re
from contextlib import asynccontextmanager
from datetime import datetime
from collections import Counter
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select, or_

_log = logging.getLogger("true_review.main")


def _forwarded_ip(request: Request) -> str:
    """Use the original client IP from X-Forwarded-For so rate limiting
    survives Railway's reverse proxy (which otherwise gives every request
    a different ephemeral 100.64.x.x source address)."""
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"

from .config import get_settings
from .db import init_db, get_session, engine
from .models import (
    Company,
    CompanyKind,
    Review,
    ReviewType,
    ModerationLog,
    User,
)
from .schemas import (
    CompanyOut,
    CompanyHealth,
    CompanySearchResult,
    CompanyIn,
    ReviewOut,
    ReviewIn,
    ScamAlertOut,
    ModerationLogOut,
)
from .seed import run_seed
from .bulk_import import bulk_import_edgar, bulk_import_wikidata, bulk_import_mediawiki
from .ai import ReviewSnippet, ask_llm
from .security import (
    sanitize_text,
    detect_problems,
    hash_ip,
    harden_prompt_input,
)
from .audit import log_event, SecurityEvent  # noqa: F401 — imported for table registration
from .enrichment import (
    fetch_wikipedia_summary,
    fetch_opencorporates,
    fetch_edgar,
    fetch_urlhaus,
)
from .email import send_otp
from .models import EmailVerification  # noqa: F401 — registers table

settings = get_settings()

limiter = Limiter(key_func=_forwarded_ip)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    from sqlmodel import Session as _Session
    with _Session(engine) as session:
        # Always run the curated seed — it's idempotent and tops up demo
        # content when we expand the SAMPLE_COMPANIES / *_REVIEWS lists.
        run_seed(session)

        # Stage 1: SEC EDGAR — every US publicly-traded operating company.
        # Stage 2: Wikidata — every globally publicly-listed company with
        #          an English label (covers LSE, TSX, TSE, DAX, ASX, NSE,
        #          Euronext, JSE, …). Both stages idempotent + non-fatal.
        count = len(session.exec(select(Company)).all())
        if count < 1500:
            try:
                result = bulk_import_edgar(session)
                _log.info("EDGAR bulk import: added=%s skipped=%s",
                          result.get("added"), result.get("skipped"))
            except Exception as e:  # noqa: BLE001 — never let import abort startup
                _log.warning("EDGAR bulk import failed (non-fatal): %s", e)
            count = len(session.exec(select(Company)).all())

        # Stage 2: Wikidata SPARQL — globally publicly-listed + privately-
        # held notable. Re-runs while under threshold so we get a top-up
        # whenever WDQS recovers from an outage.
        if count < 30_000:
            try:
                result = bulk_import_wikidata(session)
                _log.info(
                    "Wikidata bulk import: added=%s skipped=%s "
                    "listed_returned=%s private_returned=%s",
                    result.get("added"), result.get("skipped"),
                    result.get("listed_returned"), result.get("private_returned"),
                )
            except Exception as e:  # noqa: BLE001
                _log.warning("Wikidata bulk import failed (non-fatal): %s", e)
            count = len(session.exec(select(Company)).all())

        # Stage 3: MediaWiki category enumeration — fallback / supplement.
        # Uses the Action API (different endpoint than WDQS) so it works
        # even when SPARQL is rate-limited. Covers stock-exchange categories,
        # privately-held majors, and topical groupings (banks, pharma, etc.).
        if count < 30_000:
            try:
                result = bulk_import_mediawiki(session)
                _log.info(
                    "MediaWiki bulk import: added=%s skipped=%s "
                    "categories=%s raw_titles=%s",
                    result.get("added"), result.get("skipped"),
                    result.get("categories_queried"), result.get("raw_titles"),
                )
            except Exception as e:  # noqa: BLE001
                _log.warning("MediaWiki bulk import failed (non-fatal): %s", e)
    yield


app = FastAPI(
    title="True Review API",
    version="0.3.0",
    description=(
        "Verified company review platform — employment, shopping, scam reports. "
        "AI-assisted, transparently moderated, privacy-first."
    ),
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# --------------------------------------------------------------------------- #
# CORS — explicit allowlist. No regex wildcards.
# --------------------------------------------------------------------------- #
_ALLOWED_ORIGINS = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    # Preview URLs from Vercel are auto-generated. We still gate by a strict
    # regex matching only this project's preview pattern, not all of vercel.app.
    allow_origin_regex=r"^https://true-review[a-z0-9\-]*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,
)


# --------------------------------------------------------------------------- #
# Security response headers
# --------------------------------------------------------------------------- #

@app.middleware("http")
async def security_headers(request: Request, call_next):
    """Headers aligned to DISA ASD STIG V-222489 / NIST 800-53 SC-7, SC-8, SI-10."""
    try:
        response = await call_next(request)
    except Exception:
        # SI-11: never leak stack traces to clients. We DO log the full
        # traceback server-side so failures stay diagnosable.
        _log.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
        from fastapi.responses import JSONResponse
        response = JSONResponse({"error": "internal_error"}, status_code=500)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=(), payment=()"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    # API responses must not be cached by intermediaries (privacy hygiene)
    if request.url.path != "/health":
        response.headers["Cache-Control"] = "no-store"
    return response


def slugify(text: str) -> str:
    import re
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return s or uuid4().hex[:8]


# --------------------------------------------------------------------------- #
# Health + meta
# --------------------------------------------------------------------------- #

@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}


@app.get("/")
def root():
    return {
        "name": "True Review API",
        "version": app.version,
        "docs": "/docs",
        "disclaimer": (
            "Scam reports are user-submitted claims, not platform verdicts. "
            "Until a company has at least 3 independent verified reports, it is "
            "marked 'pending review' rather than 'scam'."
        ),
        "endpoints": {
            "search": "/companies?q=...",
            "company": "/companies/{slug}",
            "reviews": "/companies/{slug}/reviews",
            "submit_review": "POST /reviews",
            "ai_search": "/ai/search?q=...",
            "ai_ask": "POST /ai/ask",
            "scam_alerts": "/scam-alerts",
            "moderation_log": "/moderation/log",
        },
    }


# --------------------------------------------------------------------------- #
# Companies
# --------------------------------------------------------------------------- #

@app.get("/companies/stats")
@limiter.limit("30/minute")
def companies_stats(request: Request, session: Session = Depends(get_session)):
    """Catalog size + simple distribution. Useful for ops + audit checks."""
    from sqlalchemy import func
    total = session.exec(select(func.count(Company.id))).first() or 0
    flagged = session.exec(
        select(func.count(Company.id)).where(Company.is_scam_flagged.is_(True))
    ).first() or 0
    with_reviews = session.exec(
        select(func.count(func.distinct(Review.company_id)))
        .where(Review.is_published.is_(True))
    ).first() or 0
    reviews_total = session.exec(
        select(func.count(Review.id)).where(Review.is_published.is_(True))
    ).first() or 0
    return {
        "total_companies": int(total),
        "flagged_companies": int(flagged),
        "companies_with_reviews": int(with_reviews),
        "total_published_reviews": int(reviews_total),
    }


@app.get("/companies", response_model=list[CompanySearchResult])
@limiter.limit("120/minute")
def search_companies(
    request: Request,
    q: str = Query(""),
    kind: Optional[str] = Query(None),
    flagged: Optional[bool] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    session: Session = Depends(get_session),
):
    stmt = select(Company)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Company.name.ilike(like), Company.domain.ilike(like)))
    if kind:
        try:
            stmt = stmt.where(Company.kind == CompanyKind(kind))
        except ValueError:
            raise HTTPException(400, f"Unknown kind: {kind}")
    if flagged is True:
        stmt = stmt.where(Company.is_scam_flagged.is_(True))
    elif flagged is False:
        stmt = stmt.where(Company.is_scam_flagged.is_(False))
    stmt = stmt.limit(limit)

    rows = session.exec(stmt).all()
    out: list[CompanySearchResult] = []
    for c in rows:
        review_count = len(
            session.exec(select(Review).where(Review.company_id == c.id, Review.is_published.is_(True))).all()
        )
        out.append(
            CompanySearchResult(
                id=str(c.id),
                name=c.name,
                slug=c.slug,
                kind=c.kind.value if isinstance(c.kind, CompanyKind) else str(c.kind),
                review_count=review_count,
                is_scam_flagged=c.is_scam_flagged,
                scam_reports_count=c.scam_reports_count or 0,
            )
        )
    return out


@app.get("/companies/discover")
@limiter.limit("30/minute")
async def discover_companies_route(
    request: Request,
    q: str = Query(..., min_length=2, max_length=120),
    session: Session = Depends(get_session),
):
    """Search beyond our internal catalog.

    Returns: { internal: [...], external: [...] }

    DECLARED BEFORE /companies/{slug} so the literal path matches first;
    FastAPI evaluates routes in registration order.
    """
    safe = sanitize_text(q, max_len=120)
    like = f"%{safe}%"
    internal_rows = session.exec(
        select(Company)
        .where(or_(Company.name.ilike(like), Company.domain.ilike(like)))
        .limit(10)
    ).all()
    internal = [
        {
            "name": c.name,
            "slug": c.slug,
            "kind": c.kind.value if isinstance(c.kind, CompanyKind) else str(c.kind),
            "domain": c.domain,
            "is_scam_flagged": c.is_scam_flagged,
            "scam_reports_count": c.scam_reports_count or 0,
            "exists": True,
        }
        for c in internal_rows
    ]
    have_slugs = {c["slug"] for c in internal}

    wiki = await fetch_wikipedia_summary(safe)
    oc = await fetch_opencorporates(safe)

    external = []
    if wiki.get("found"):
        proposed_slug = slugify(wiki.get("title") or safe)
        if proposed_slug not in have_slugs:
            external.append({
                "source": "wikipedia",
                "name": wiki.get("title"),
                "proposed_slug": proposed_slug,
                "description": (wiki.get("extract") or "")[:280],
                "url": wiki.get("url"),
                "exists": False,
            })
    for m in (oc.get("matches") or [])[:3]:
        name = m.get("name")
        if not name:
            continue
        proposed_slug = slugify(name)
        if proposed_slug in have_slugs:
            continue
        external.append({
            "source": "opencorporates",
            "name": name,
            "proposed_slug": proposed_slug,
            "jurisdiction": m.get("jurisdiction"),
            "registration_number": m.get("number"),
            "status": m.get("status"),
            "url": m.get("opencorporates_url"),
            "exists": False,
        })

    return {"query": safe, "internal": internal, "external": external}


@app.get("/companies/{slug}", response_model=CompanyOut)
@limiter.limit("180/minute")
def get_company(request: Request, slug: str, session: Session = Depends(get_session)):
    company = session.exec(select(Company).where(Company.slug == slug)).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    reviews = session.exec(
        select(Review).where(Review.company_id == company.id, Review.is_published.is_(True))
    ).all()

    employment_reviews = [r for r in reviews if r.review_type == ReviewType.EMPLOYMENT]
    shopping_reviews = [r for r in reviews if r.review_type == ReviewType.SHOPPING]
    scam_reports = [r for r in reviews if r.review_type == ReviewType.SCAM_REPORT]

    non_scam = employment_reviews + shopping_reviews
    sentiment = (
        sum(r.rating_overall for r in non_scam) / (len(non_scam) * 5.0) if non_scam else 0.5
    )
    layoff_risk = min(1.0, len(scam_reports) * 0.15 + (0.2 if company.is_scam_flagged else 0.05))

    return CompanyOut(
        id=str(company.id),
        name=company.name,
        slug=company.slug,
        kind=company.kind.value if isinstance(company.kind, CompanyKind) else str(company.kind),
        trust_score=max(0.0, 1.0 - (company.scam_severity or 0.0)),
        review_count=len(reviews),
        employment_review_count=len(employment_reviews),
        shopping_review_count=len(shopping_reviews),
        scam_report_count=len(scam_reports),
        is_scam_flagged=company.is_scam_flagged,
        scam_severity=company.scam_severity or 0.0,
        health=CompanyHealth(
            sentiment=sentiment,
            layoff_risk=layoff_risk,
            leadership_confidence=sentiment * 0.9,
        ),
        ai_summary=None,
        description=company.description,
        domain=company.domain,
    )


@app.get("/companies/{slug}/reviews", response_model=list[ReviewOut])
@limiter.limit("120/minute")
def list_company_reviews(
    request: Request,
    slug: str,
    review_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    session: Session = Depends(get_session),
):
    company = session.exec(select(Company).where(Company.slug == slug)).first()
    if not company:
        raise HTTPException(404, "Company not found")

    stmt = select(Review).where(Review.company_id == company.id, Review.is_published.is_(True))
    if review_type:
        try:
            stmt = stmt.where(Review.review_type == ReviewType(review_type))
        except ValueError:
            raise HTTPException(400, f"Unknown review_type: {review_type}")
    stmt = stmt.order_by(Review.created_at.desc()).limit(limit)
    rows = session.exec(stmt).all()

    out: list[ReviewOut] = []
    for r in rows:
        author = (
            session.exec(select(User).where(User.id == r.author_id)).first()
            if r.author_id
            else None
        )
        tier = author.verification_tier if author else None
        out.append(
            ReviewOut(
                id=str(r.id),
                review_type=r.review_type.value if isinstance(r.review_type, ReviewType) else str(r.review_type),
                title=r.title,
                body=r.body,
                rating_overall=r.rating_overall,
                department=r.department,
                location=r.location,
                product_or_service=r.product_or_service,
                purchase_amount=r.purchase_amount,
                scam_category=r.scam_category,
                money_lost=r.money_lost,
                created_at=r.created_at.isoformat(),
                author_handle=author.handle if author else None,
                author_verification_tier=(tier.value if hasattr(tier, "value") else (str(tier) if tier else None)),
                verification_source=_verification_source_label(tier, r.is_demo),
                verification_explainer=_verification_explainer(tier, r.is_demo),
                is_demo=r.is_demo,
            )
        )
    return out


def _verification_source_label(tier, is_demo: bool) -> str:
    if is_demo:
        return "Demo content"
    if tier is None or (hasattr(tier, "value") and tier.value == "none"):
        return "Unverified"
    label_map = {
        "t1_email": "Work email verified",
        "t2_linkedin": "LinkedIn verified",
        "t3_document": "Document verified",
        "t4_payroll": "Payroll verified",
        "t_receipt": "Receipt verified",
        "t_fraud_evidence": "Evidence on file",
    }
    tv = tier.value if hasattr(tier, "value") else str(tier)
    return label_map.get(tv, "Verified")


def _verification_explainer(tier, is_demo: bool) -> str:
    if is_demo:
        return (
            "This is illustrative seed content used to demonstrate the platform. "
            "Once verified users start posting, demo content gets retired."
        )
    if tier is None or (hasattr(tier, "value") and tier.value == "none"):
        return (
            "This reviewer hasn't completed identity verification. Treat the "
            "claim with the same skepticism you'd apply to any anonymous post."
        )
    explain_map = {
        "t1_email": (
            "The reviewer proved they own a mailbox at the company's domain via a "
            "one-time email code. Their address is stored only as a salted hash."
        ),
        "t2_linkedin": (
            "We confirmed the reviewer's LinkedIn employment matched the company "
            "at the time of posting, without sharing their profile publicly."
        ),
        "t3_document": (
            "A human verifier reviewed a redacted document (W-2, offer letter, or "
            "pay stub) proving the employment relationship."
        ),
        "t4_payroll": (
            "The reviewer connected a payroll provider (Argyle/Pinwheel) that "
            "cryptographically attested employment. Employer is never notified."
        ),
        "t_receipt": (
            "The reviewer uploaded a redacted receipt or order confirmation as "
            "proof of purchase."
        ),
        "t_fraud_evidence": (
            "The reviewer attached evidence of the fraud (charge dispute, "
            "transaction ID, ticket reference). Reviewed by our moderation team."
        ),
    }
    tv = tier.value if hasattr(tier, "value") else str(tier)
    return explain_map.get(tv, "Verification source not specified.")


# --------------------------------------------------------------------------- #
# Submitting reviews + scam reports — rate limited + sanitized + content gated
# --------------------------------------------------------------------------- #

@app.post("/reviews", response_model=ReviewOut, status_code=201)
@limiter.limit("5/minute;20/hour;100/day")
def submit_review(
    request: Request,
    body: ReviewIn,
    session: Session = Depends(get_session),
):
    safe_title = sanitize_text(body.title, max_len=200)
    safe_body = sanitize_text(body.body, max_len=5000)
    if len(safe_body) < 20:
        raise HTTPException(422, "Review body too short after sanitization (min 20 chars).")

    problems = detect_problems(safe_title + "\n" + safe_body)
    if problems:
        raise HTTPException(
            422,
            {
                "error": "content_rejected",
                "problems": problems,
                "explanation": (
                    "Posts must not include personally identifying info (SSN, payment "
                    "cards, email, phone) or accusations naming specific individuals."
                ),
            },
        )

    company = session.exec(select(Company).where(Company.slug == body.company_slug)).first()
    if not company:
        company = Company(
            slug=slugify(body.company_slug),
            name=body.company_slug.replace("-", " ").title(),
            kind=CompanyKind.BOTH,
        )
        session.add(company)
        session.flush()

    # Anonymous-by-default. We refuse user-supplied handles to prevent impersonation.
    handle = f"anon-{uuid4().hex[:8]}"
    user = User(handle=handle)
    session.add(user)
    session.flush()

    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else None)
    ip_h = hash_ip(ip)

    review = Review(
        company_id=company.id,
        author_id=user.id,
        review_type=ReviewType(body.review_type),
        title=safe_title,
        body=safe_body,
        rating_overall=body.rating_overall,
        department=sanitize_text(body.department or "", max_len=80) or None,
        location=sanitize_text(body.location or "", max_len=80) or None,
        job_level=sanitize_text(body.job_level or "", max_len=80) or None,
        employment_status=body.employment_status,
        product_or_service=sanitize_text(body.product_or_service or "", max_len=120) or None,
        purchase_amount=body.purchase_amount,
        scam_category=body.scam_category,
        money_lost=body.money_lost,
        submitter_ip_hash=ip_h,
    )
    session.add(review)

    if review.review_type == ReviewType.SCAM_REPORT:
        company.scam_reports_count = (company.scam_reports_count or 0) + 1
        company.last_scam_report_at = datetime.utcnow()

        # Count distinct submitter ip hashes for scam reports against this company
        scam_rows = session.exec(
            select(Review).where(
                Review.company_id == company.id, Review.review_type == ReviewType.SCAM_REPORT
            )
        ).all()
        distinct_submitters = {r.submitter_ip_hash for r in scam_rows if r.submitter_ip_hash}
        # Auto-flag ONLY if we have N distinct submitters past threshold. Otherwise
        # the company stays "pending review" — never a public "scam" label from a
        # single submitter. This is critical defamation hygiene.
        threshold = company.flag_review_threshold or 3
        if len(distinct_submitters) >= threshold:
            company.is_scam_flagged = True
            company.scam_severity = min(1.0, 0.4 + 0.08 * len(distinct_submitters))
        session.add(company)

    log_event(
        session,
        event_type=(
            "scam_report_submitted"
            if review.review_type == ReviewType.SCAM_REPORT
            else "review_submitted"
        ),
        actor_ip_hash=ip_h,
        target_id=str(review.id),
        payload={
            "company_slug": company.slug,
            "review_type": review.review_type.value,
            "rating_overall": review.rating_overall,
        },
    )
    session.commit()
    session.refresh(review)

    return ReviewOut(
        id=str(review.id),
        review_type=review.review_type.value,
        title=review.title,
        body=review.body,
        rating_overall=review.rating_overall,
        department=review.department,
        location=review.location,
        product_or_service=review.product_or_service,
        purchase_amount=review.purchase_amount,
        scam_category=review.scam_category,
        money_lost=review.money_lost,
        created_at=review.created_at.isoformat(),
        author_handle=user.handle,
    )


# --------------------------------------------------------------------------- #
# External enrichment — real public data
# --------------------------------------------------------------------------- #

@app.post("/companies", response_model=CompanyOut, status_code=201)
@limiter.limit("10/minute;50/day")
def create_company(request: Request, body: CompanyIn, session: Session = Depends(get_session)):
    slug = body.slug or slugify(body.name)
    if session.exec(select(Company).where(Company.slug == slug)).first():
        raise HTTPException(409, f"Company with slug '{slug}' already exists")
    company = Company(
        slug=slug,
        name=sanitize_text(body.name, max_len=200),
        kind=CompanyKind(body.kind),
        domain=sanitize_text(body.domain or "", max_len=200) or None,
        description=sanitize_text(body.description or "", max_len=2000) or None,
    )
    session.add(company)
    session.commit()
    session.refresh(company)
    return get_company(request, slug, session)


@app.get("/enrichment/wikipedia")
@limiter.limit("60/minute")
async def enrichment_wikipedia(request: Request, name: str = Query(..., min_length=2, max_length=120)):
    return await fetch_wikipedia_summary(sanitize_text(name, max_len=120))


@app.get("/enrichment/opencorporates")
@limiter.limit("30/minute")
async def enrichment_opencorporates(request: Request, name: str = Query(..., min_length=2, max_length=120)):
    return await fetch_opencorporates(sanitize_text(name, max_len=120))


@app.get("/enrichment/edgar")
@limiter.limit("30/minute")
async def enrichment_edgar(request: Request, name: str = Query(..., min_length=2, max_length=120)):
    return await fetch_edgar(sanitize_text(name, max_len=120))


@app.get("/enrichment/urlhaus")
@limiter.limit("60/minute")
async def enrichment_urlhaus(request: Request, domain: str = Query(..., min_length=3, max_length=253)):
    return await fetch_urlhaus(sanitize_text(domain, max_len=253).lower())


@app.get("/scam-check")
@limiter.limit("30/minute")
async def scam_check(
    request: Request,
    domain: str = Query(..., min_length=3, max_length=253),
    session: Session = Depends(get_session),
):
    """Combined scam check: internal reports + URLhaus.

    Returns the verdict + evidence with cited sources so the UI can
    present it neutrally.
    """
    safe = sanitize_text(domain, max_len=253).lower().strip()
    safe = safe.replace("https://", "").replace("http://", "").split("/")[0]

    # Internal — match company by domain (exact) or by slug containing domain root.
    internal = session.exec(
        select(Company).where(Company.domain == safe)
    ).first()
    internal_reports = 0
    if internal:
        internal_reports = len(
            session.exec(
                select(Review).where(
                    Review.company_id == internal.id,
                    Review.review_type == ReviewType.SCAM_REPORT,
                    Review.is_published.is_(True),
                )
            ).all()
        )

    urlhaus = await fetch_urlhaus(safe)

    verdict = "no_signal"
    if (internal and internal.is_scam_flagged) or urlhaus.get("found"):
        verdict = "flagged"
    elif internal_reports > 0:
        verdict = "pending_review"

    return {
        "domain": safe,
        "verdict": verdict,
        "internal": {
            "company": {
                "name": internal.name,
                "slug": internal.slug,
                "is_scam_flagged": internal.is_scam_flagged,
                "scam_reports_count": internal.scam_reports_count or 0,
            } if internal else None,
            "report_count": internal_reports,
        },
        "urlhaus": urlhaus,
    }


# --------------------------------------------------------------------------- #
# Workplace verifier — T1 work-email OTP
# --------------------------------------------------------------------------- #

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "proton.me", "protonmail.com", "live.com", "msn.com",
    "ymail.com", "gmx.com", "mail.com", "fastmail.com",
}


def _otp() -> str:
    import secrets
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash(value: str) -> str:
    import hashlib
    salt = os.environ.get("VERIFY_HASH_SALT", "true-review-verify-salt-rotate-me")
    return hashlib.sha256(f"{salt}::{value}".encode()).hexdigest()

@app.post("/verify/email/start")
@limiter.limit("3/minute;15/day")
async def verify_email_start(
    request: Request,
    body: dict,
    session: Session = Depends(get_session),
):
    """Begin work-email verification.

    Body: { email, company_slug? }

    Free webmail domains (gmail, yahoo, etc.) are rejected — T1 is meant
    to prove employment via a company-issued mailbox. We hash the email
    before storing it (the DB never holds the raw value).
    """
    email = sanitize_text((body or {}).get("email", ""), max_len=200).strip().lower()
    company_slug = sanitize_text((body or {}).get("company_slug", ""), max_len=200).strip().lower() or None

    if "@" not in email or len(email) < 6:
        raise HTTPException(400, "Valid email required")
    domain = email.rsplit("@", 1)[-1]
    if domain in FREE_EMAIL_DOMAINS:
        raise HTTPException(
            400,
            "Free webmail domains (gmail, yahoo, etc.) are not accepted for T1 verification. "
            "Use your work email.",
        )
    if not re.fullmatch(r"[a-zA-Z0-9.-]{3,253}", domain):
        raise HTTPException(400, "Invalid domain")

    company_name = None
    if company_slug:
        c = session.exec(select(Company).where(Company.slug == company_slug)).first()
        if c:
            company_name = c.name

    from uuid import uuid4
    token = uuid4().hex
    otp = _otp()
    from datetime import timedelta
    record = EmailVerification(
        token=token,
        email_hash=_hash(email),
        domain=domain,
        company_slug=company_slug,
        otp_hash=_hash(otp),
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    session.add(record)

    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else None)
    log_event(
        session,
        event_type="verify_email_start",
        actor_ip_hash=hash_ip(ip),
        target_id=token,
        payload={"domain": domain, "company_slug": company_slug},
    )
    session.commit()

    result = await send_otp(email, otp, company_name=company_name)
    return {
        "token": token,
        "domain": domain,
        "expires_in_seconds": 600,
        "email_sent": result.get("sent", False),
        "delivery": result.get("channel"),
        "delivery_error": result.get("error"),
    }


@app.post("/verify/email/confirm")
@limiter.limit("10/minute;30/day")
async def verify_email_confirm(
    request: Request,
    body: dict,
    session: Session = Depends(get_session),
):
    """Confirm OTP. Body: { token, otp }"""
    token = sanitize_text((body or {}).get("token", ""), max_len=64)
    otp = sanitize_text((body or {}).get("otp", ""), max_len=12).strip()
    if not token or not re.fullmatch(r"\d{6}", otp):
        raise HTTPException(400, "token and 6-digit otp required")

    rec = session.exec(select(EmailVerification).where(EmailVerification.token == token)).first()
    if not rec:
        raise HTTPException(404, "verification not found")
    if rec.consumed_at:
        raise HTTPException(410, "verification already used")
    if rec.expires_at < datetime.utcnow():
        raise HTTPException(410, "verification expired")
    if rec.attempts >= 5:
        raise HTTPException(429, "too many attempts")
    import re as _re

    rec.attempts += 1
    if _hash(otp) != rec.otp_hash:
        session.add(rec)
        session.commit()
        raise HTTPException(401, "incorrect code")

    rec.consumed_at = datetime.utcnow()
    session.add(rec)

    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else None)
    log_event(
        session,
        event_type="verify_email_confirm",
        actor_ip_hash=hash_ip(ip),
        target_id=token,
        payload={"domain": rec.domain, "company_slug": rec.company_slug},
    )
    session.commit()

    return {
        "verified": True,
        "domain": rec.domain,
        "company_slug": rec.company_slug,
        "tier": "t1_email",
    }


# --------------------------------------------------------------------------- #
# DSA Notice & Action — public content-report endpoint
# --------------------------------------------------------------------------- #

@app.post("/notice-action")
@limiter.limit("3/minute;30/day")
def notice_action(request: Request, body: dict, session: Session = Depends(get_session)):
    """EU Digital Services Act Article 16 'Notice and Action' endpoint.

    Accepts a structured complaint about specific content. We log it as a
    security event for the moderation queue.
    """
    target_id = sanitize_text((body or {}).get("review_id", ""), max_len=64)
    reason = sanitize_text((body or {}).get("reason", ""), max_len=200)
    details = sanitize_text((body or {}).get("details", ""), max_len=2000)
    reporter_contact = sanitize_text((body or {}).get("reporter_contact", ""), max_len=200)
    if not reason or not details:
        raise HTTPException(400, "reason and details are required")

    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else None)
    log_event(
        session,
        event_type="notice_and_action",
        actor_ip_hash=hash_ip(ip),
        target_id=target_id or None,
        payload={"reason": reason, "details": details, "reporter_contact": reporter_contact},
    )
    session.commit()
    return {"status": "received", "expected_response_within_days": 7}


# --------------------------------------------------------------------------- #
# AI copilot — rate limited + prompt-injection hardened
# --------------------------------------------------------------------------- #

@app.post("/ai/ask")
@limiter.limit("10/minute;100/day")
async def ai_ask(
    request: Request,
    body: dict,
    session: Session = Depends(get_session),
):
    question = sanitize_text((body or {}).get("question", ""), max_len=500)
    if not question or len(question.strip()) < 3:
        raise HTTPException(400, "question is required (>=3 chars)")
    company_slug = (body or {}).get("company_slug")
    limit = min(int((body or {}).get("limit", 60) or 60), 80)

    if company_slug:
        company = session.exec(select(Company).where(Company.slug == company_slug)).first()
        if not company:
            raise HTTPException(404, "Company not found")
        company_name = company.name
        rows = session.exec(
            select(Review)
            .where(Review.company_id == company.id, Review.is_published.is_(True))
            .order_by(Review.created_at.desc())
            .limit(limit)
        ).all()
    else:
        company_name = None
        rows = session.exec(
            select(Review).where(Review.is_published.is_(True))
            .order_by(Review.created_at.desc())
            .limit(limit)
        ).all()

    snippets = [
        ReviewSnippet(
            title=harden_prompt_input(r.title, max_len=200),
            body=harden_prompt_input(r.body, max_len=2000),
            review_type=r.review_type.value if isinstance(r.review_type, ReviewType) else str(r.review_type),
            rating=r.rating_overall,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
    result = await ask_llm(harden_prompt_input(question, max_len=500), snippets, company_name=company_name)
    return result


@app.get("/ai/search")
@limiter.limit("15/minute;200/day")
async def ai_search(
    request: Request,
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(8, ge=1, le=25),
    session: Session = Depends(get_session),
):
    safe_q = sanitize_text(q, max_len=200)
    like = f"%{safe_q}%"
    rows = session.exec(
        select(Company)
        .where(or_(Company.name.ilike(like), Company.description.ilike(like), Company.domain.ilike(like)))
        .limit(limit)
    ).all()

    review_hits = session.exec(
        select(Review).where(Review.body.ilike(like)).order_by(Review.created_at.desc()).limit(limit * 2)
    ).all()
    seen = {c.id for c in rows}
    for r in review_hits:
        if r.company_id in seen:
            continue
        c = session.exec(select(Company).where(Company.id == r.company_id)).first()
        if c:
            rows.append(c)
            seen.add(c.id)
        if len(rows) >= limit:
            break

    companies_out = []
    snippets: list[ReviewSnippet] = []
    for c in rows[:limit]:
        c_reviews = session.exec(
            select(Review).where(Review.company_id == c.id, Review.is_published.is_(True))
            .order_by(Review.created_at.desc())
            .limit(8)
        ).all()
        for r in c_reviews:
            snippets.append(
                ReviewSnippet(
                    title=harden_prompt_input(f"{c.name}: {r.title}", max_len=240),
                    body=harden_prompt_input(r.body, max_len=2000),
                    review_type=r.review_type.value if isinstance(r.review_type, ReviewType) else str(r.review_type),
                    rating=r.rating_overall,
                    created_at=r.created_at.isoformat(),
                )
            )
        companies_out.append({
            "id": str(c.id),
            "name": c.name,
            "slug": c.slug,
            "kind": c.kind.value if isinstance(c.kind, CompanyKind) else str(c.kind),
            "is_scam_flagged": c.is_scam_flagged,
            "scam_reports_count": c.scam_reports_count or 0,
            "review_count": len(c_reviews),
        })

    summary = await ask_llm(harden_prompt_input(safe_q, max_len=200), snippets) if snippets else {
        "answer": "No companies matched. Try a broader search term or browse Scam Alerts.",
        "citations": [],
        "source": "fallback",
        "model": "keyword",
    }
    return {"query": safe_q, "companies": companies_out, "summary": summary}


# --------------------------------------------------------------------------- #
# Scam alerts
# --------------------------------------------------------------------------- #

@app.get("/scam-alerts", response_model=list[ScamAlertOut])
@limiter.limit("60/minute")
def scam_alerts(
    request: Request,
    limit: int = Query(25, ge=1, le=100),
    session: Session = Depends(get_session),
):
    flagged = session.exec(
        select(Company)
        .where(Company.is_scam_flagged.is_(True))
        .order_by(Company.scam_severity.desc(), Company.scam_reports_count.desc())
        .limit(limit)
    ).all()
    out: list[ScamAlertOut] = []
    for c in flagged:
        reports = session.exec(
            select(Review).where(
                Review.company_id == c.id, Review.review_type == ReviewType.SCAM_REPORT
            )
        ).all()
        categories = [r.scam_category for r in reports if r.scam_category]
        top = [cat for cat, _ in Counter(categories).most_common(3)]
        out.append(
            ScamAlertOut(
                id=str(c.id),
                name=c.name,
                slug=c.slug,
                scam_reports_count=c.scam_reports_count or len(reports),
                scam_severity=c.scam_severity or 0.0,
                last_scam_report_at=(
                    c.last_scam_report_at.isoformat() if c.last_scam_report_at else None
                ),
                top_categories=top,
            )
        )
    return out


# --------------------------------------------------------------------------- #
# Moderation log
# --------------------------------------------------------------------------- #

@app.get("/moderation/log", response_model=list[ModerationLogOut])
@limiter.limit("60/minute")
def moderation_log(request: Request, session: Session = Depends(get_session)):
    rows = session.exec(
        select(ModerationLog).order_by(ModerationLog.created_at.desc()).limit(100)
    ).all()
    return [
        ModerationLogOut(
            id=str(r.id),
            review_id=str(r.review_id) if r.review_id else None,
            action=r.action,
            reason=r.reason,
            moderator_handle=r.moderator_handle,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
