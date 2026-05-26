from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .config import get_settings
from .db import init_db, get_session
from .models import Company, Review, ModerationLog
from .schemas import (
    CompanyOut,
    CompanyHealth,
    CompanySearchResult,
    ModerationLogOut,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="True Review API",
    version="0.1.0",
    description="AI-native company review platform — verified, transparent, privacy-first.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/companies", response_model=list[CompanySearchResult])
def search_companies(q: str = Query(""), session: Session = Depends(get_session)):
    if not q:
        return []
    stmt = select(Company).where(Company.name.ilike(f"%{q}%")).limit(20)
    rows = session.exec(stmt).all()
    out: list[CompanySearchResult] = []
    for c in rows:
        review_count = len(
            session.exec(select(Review).where(Review.company_id == c.id)).all()
        )
        out.append(
            CompanySearchResult(
                id=str(c.id), name=c.name, slug=c.slug, review_count=review_count
            )
        )
    return out


@app.get("/companies/{slug}", response_model=CompanyOut)
def get_company(slug: str, session: Session = Depends(get_session)):
    company = session.exec(select(Company).where(Company.slug == slug)).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    reviews = session.exec(select(Review).where(Review.company_id == company.id)).all()
    review_count = len(reviews)

    # Stubbed analytics — replaced with real AI pipeline in M4.
    if reviews:
        sentiment = sum(r.rating_overall for r in reviews) / (review_count * 5.0)
    else:
        sentiment = 0.5

    return CompanyOut(
        id=str(company.id),
        name=company.name,
        slug=company.slug,
        trust_score=0.5,
        review_count=review_count,
        health=CompanyHealth(
            sentiment=sentiment,
            layoff_risk=0.2,
            leadership_confidence=sentiment * 0.9,
        ),
        ai_summary=None,
    )


@app.get("/moderation/log", response_model=list[ModerationLogOut])
def moderation_log(session: Session = Depends(get_session)):
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


@app.get("/")
def root():
    return {
        "name": "True Review API",
        "version": "0.1.0",
        "docs": "/docs",
    }
