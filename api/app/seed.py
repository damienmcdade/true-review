"""Seed the database with **clearly demonstrative** companies + reviews.

LEGAL NOTE:
- All seed data is marked `is_demo=True`. Frontend shows a "DEMO" badge.
- We avoid attributing specific opinions to real, named companies. Real
  brand names appear ONLY in neutral "this is the company being reviewed"
  context, never as endorsements of negative claims. Pre-built reviews use
  carefully worded, opinion-coded statements that any reasonable reader
  would identify as illustrative.
- Scam-flagged seed entries use unmistakably fictional names with `-demo`
  suffix so they can never be mistaken for real businesses.

This file is idempotent — safe to re-run on every boot.
"""
from datetime import datetime
from uuid import uuid4

from sqlmodel import Session, select

from .models import Company, CompanyKind, Review, ReviewType, User, VerificationTier


# Real public companies used only as neutral search targets. Their seeded
# reviews are deliberately mild, balanced, and clearly demo content.
SAMPLE_COMPANIES = [
    {"name": "Stripe", "slug": "stripe", "kind": "employer", "domain": "stripe.com",
     "description": "Payments infrastructure for the internet."},
    {"name": "Anthropic", "slug": "anthropic", "kind": "employer", "domain": "anthropic.com",
     "description": "AI safety company that builds Claude."},
    {"name": "Shopify", "slug": "shopify", "kind": "both", "domain": "shopify.com",
     "description": "Commerce platform powering millions of merchants."},
    {"name": "Patagonia", "slug": "patagonia", "kind": "both", "domain": "patagonia.com",
     "description": "Outdoor apparel; mission-driven sustainability brand."},
    {"name": "Costco", "slug": "costco", "kind": "merchant", "domain": "costco.com",
     "description": "Membership warehouse retailer."},
    {"name": "Apple", "slug": "apple", "kind": "both", "domain": "apple.com",
     "description": "Consumer electronics and services."},
    {"name": "Microsoft", "slug": "microsoft", "kind": "employer", "domain": "microsoft.com",
     "description": "Software, cloud, devices."},
    {"name": "Netflix", "slug": "netflix", "kind": "employer", "domain": "netflix.com",
     "description": "Streaming entertainment service."},
    # Fictional scam-flagged demos (clearly marked, can never be confused with real companies)
    {"name": "Acme Phishing Demo Co", "slug": "acme-phishing-demo",
     "kind": "merchant", "domain": "acme-phishing-demo.example",
     "description": "FICTIONAL demonstration entity used to showcase the scam-report flow.",
     "is_scam_flagged": True, "scam_severity": 0.88},
    {"name": "ExampleScam Industries Demo", "slug": "examplescam-industries-demo",
     "kind": "merchant", "domain": "examplescam-industries-demo.example",
     "description": "FICTIONAL demonstration entity used to showcase the scam-report flow.",
     "is_scam_flagged": True, "scam_severity": 0.92},
]

# Mild, balanced demo reviews. All marked is_demo=True.
EMPLOYMENT_REVIEWS = [
    ("stripe", 4.2, "Demo review — high engineering bar",
     "Demo content for product preview. Generally positive sentiment around technical excellence and pace.", "Engineering", "current"),
    ("anthropic", 4.6, "Demo review — research culture",
     "Demo content for product preview. Generally positive sentiment around mission alignment.", "Research", "current"),
    ("shopify", 4.0, "Demo review — strong autonomy",
     "Demo content for product preview. Mixed sentiment around recent organizational changes.", "Product", "current"),
    ("microsoft", 4.1, "Demo review — steady environment",
     "Demo content for product preview. Generally positive sentiment around work-life balance.", "Engineering", "current"),
    ("netflix", 3.5, "Demo review — high autonomy, high stakes",
     "Demo content for product preview. Mixed sentiment around the performance culture.", "Engineering", "current"),
    ("patagonia", 4.6, "Demo review — mission-driven",
     "Demo content for product preview. Generally positive sentiment around values alignment.", "Retail", "current"),
]

SHOPPING_REVIEWS = [
    ("patagonia", 4.8, "Demo review — durable goods",
     "Demo content for product preview. Generally positive sentiment around product longevity and warranty service.", "Down jacket", 280.0),
    ("costco", 4.5, "Demo review — bulk value",
     "Demo content for product preview. Generally positive sentiment around membership value and return policy.", "Executive membership", 130.0),
    ("apple", 4.2, "Demo review — in-store support",
     "Demo content for product preview. Positive on in-store support; mixed on online support routing.", "Laptop", 1299.0),
    ("shopify", 4.3, "Demo review — merchant platform",
     "Demo content for product preview. Generally positive sentiment around platform reliability.", "Shopify Basic plan", 39.0),
]

# Scam reports ONLY against fictional demo entities.
SCAM_REPORTS = [
    ("acme-phishing-demo", 1.0, "Demo — non-delivery scenario",
     "FICTIONAL demo content. Illustrates how a non-delivery scam report appears on the platform.",
     "non_delivery", 89.0),
    ("acme-phishing-demo", 1.0, "Demo — phishing follow-up scenario",
     "FICTIONAL demo content. Illustrates how a phishing-followup report appears.",
     "phishing", 0.0),
    ("acme-phishing-demo", 1.0, "Demo — counterfeit scenario",
     "FICTIONAL demo content. Illustrates a counterfeit-product report.",
     "counterfeit", 145.0),
    ("examplescam-industries-demo", 1.0, "Demo — fund-withdrawal scenario",
     "FICTIONAL demo content. Illustrates a fake-investment platform report.",
     "fake_invoice", 2000.0),
    ("examplescam-industries-demo", 1.0, "Demo — deepfake-endorsement scenario",
     "FICTIONAL demo content. Illustrates a fake-celebrity-endorsement report.",
     "phishing", 0.0),
    ("examplescam-industries-demo", 1.0, "Demo — third report demonstrating threshold",
     "FICTIONAL demo content. Demonstrates that auto-flag requires multiple reports.",
     "fake_invoice", 1500.0),
]


def ensure_user(session: Session, handle: str) -> User:
    existing = session.exec(select(User).where(User.handle == handle)).first()
    if existing:
        return existing
    user = User(handle=handle, trust_score=0.7, verification_tier=VerificationTier.T1_EMAIL)
    session.add(user)
    session.flush()
    return user


def run_seed(session: Session) -> dict:
    added_companies = 0
    added_reviews = 0

    for c in SAMPLE_COMPANIES:
        existing = session.exec(select(Company).where(Company.slug == c["slug"])).first()
        if existing:
            continue
        company = Company(
            slug=c["slug"],
            name=c["name"],
            kind=CompanyKind(c["kind"]),
            domain=c.get("domain"),
            description=c.get("description"),
            is_scam_flagged=c.get("is_scam_flagged", False),
            scam_severity=c.get("scam_severity", 0.0),
        )
        session.add(company)
        added_companies += 1

    session.commit()

    author = ensure_user(session, "demo_anon")

    def add_review(slug: str, kind: ReviewType, rating: float, title: str, body: str, **kw) -> None:
        nonlocal added_reviews
        company = session.exec(select(Company).where(Company.slug == slug)).first()
        if not company:
            return
        existing = session.exec(
            select(Review).where(Review.company_id == company.id, Review.title == title)
        ).first()
        if existing:
            return
        review = Review(
            company_id=company.id,
            author_id=author.id,
            review_type=kind,
            title=title,
            body=body,
            rating_overall=rating,
            is_demo=True,
            **kw,
        )
        session.add(review)
        if kind == ReviewType.SCAM_REPORT:
            company.scam_reports_count = (company.scam_reports_count or 0) + 1
            company.last_scam_report_at = datetime.utcnow()
            # Only set is_scam_flagged on demo entities (already flagged via SAMPLE_COMPANIES).
            session.add(company)
        added_reviews += 1

    for slug, rating, title, body, dept, status in EMPLOYMENT_REVIEWS:
        add_review(slug, ReviewType.EMPLOYMENT, rating, title, body,
                   department=dept, employment_status=status)
    for slug, rating, title, body, product, amount in SHOPPING_REVIEWS:
        add_review(slug, ReviewType.SHOPPING, rating, title, body,
                   product_or_service=product, purchase_amount=amount)
    for slug, rating, title, body, category, amount in SCAM_REPORTS:
        add_review(slug, ReviewType.SCAM_REPORT, rating, title, body,
                   scam_category=category, money_lost=amount)

    session.commit()
    return {"added_companies": added_companies, "added_reviews": added_reviews}
