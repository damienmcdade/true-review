from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class CompanyHealth(BaseModel):
    sentiment: float
    layoff_risk: float
    leadership_confidence: float


class CompanyOut(BaseModel):
    id: str
    name: str
    slug: str
    kind: str
    trust_score: float
    review_count: int
    employment_review_count: int
    shopping_review_count: int
    scam_report_count: int
    is_scam_flagged: bool
    scam_severity: float
    health: CompanyHealth
    ai_summary: Optional[str] = None
    description: Optional[str] = None
    domain: Optional[str] = None


class CompanySearchResult(BaseModel):
    id: str
    name: str
    slug: str
    kind: str
    review_count: int
    is_scam_flagged: bool
    scam_reports_count: int


class ReviewOut(BaseModel):
    id: str
    review_type: str
    title: str
    body: str
    rating_overall: float
    department: Optional[str] = None
    location: Optional[str] = None
    product_or_service: Optional[str] = None
    purchase_amount: Optional[float] = None
    scam_category: Optional[str] = None
    money_lost: Optional[float] = None
    created_at: str
    author_handle: Optional[str] = None


class ReviewIn(BaseModel):
    company_slug: str
    review_type: Literal["employment", "shopping", "scam_report"]
    title: str = Field(min_length=4, max_length=200)
    body: str = Field(min_length=20, max_length=5000)
    rating_overall: float = Field(ge=1.0, le=5.0)

    # Employment
    department: Optional[str] = None
    location: Optional[str] = None
    job_level: Optional[str] = None
    employment_status: Optional[Literal["current", "former"]] = None

    # Shopping
    product_or_service: Optional[str] = None
    purchase_amount: Optional[float] = None

    # Scam report
    scam_category: Optional[
        Literal[
            "fake_product",
            "non_delivery",
            "phishing",
            "fake_job",
            "fake_invoice",
            "subscription_trap",
            "counterfeit",
            "other",
        ]
    ] = None
    money_lost: Optional[float] = None
    author_handle: Optional[str] = None  # anonymous-by-default


class CompanyIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: Optional[str] = None
    kind: Literal["employer", "merchant", "both"] = "both"
    domain: Optional[str] = None
    description: Optional[str] = None


class ScamAlertOut(BaseModel):
    id: str
    name: str
    slug: str
    scam_reports_count: int
    scam_severity: float
    last_scam_report_at: Optional[str]
    top_categories: list[str]


class ModerationLogOut(BaseModel):
    id: str
    review_id: Optional[str]
    action: str
    reason: str
    moderator_handle: str
    created_at: str
