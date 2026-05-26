from pydantic import BaseModel
from typing import Optional


class CompanyHealth(BaseModel):
    sentiment: float
    layoff_risk: float
    leadership_confidence: float


class CompanyOut(BaseModel):
    id: str
    name: str
    slug: str
    trust_score: float
    review_count: int
    health: CompanyHealth
    ai_summary: Optional[str] = None


class CompanySearchResult(BaseModel):
    id: str
    name: str
    slug: str
    review_count: int


class ReviewIn(BaseModel):
    company_slug: str
    title: str
    body: str
    department: Optional[str] = None
    location: Optional[str] = None
    rating_overall: float
    rating_culture: float
    rating_management: float
    rating_balance: float
    rating_growth: float
    rating_pay: float


class ModerationLogOut(BaseModel):
    id: str
    review_id: Optional[str]
    action: str
    reason: str
    moderator_handle: str
    created_at: str
