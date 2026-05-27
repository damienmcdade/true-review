from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class VerificationTier(str, Enum):
    NONE = "none"
    T1_EMAIL = "t1_email"
    T2_LINKEDIN = "t2_linkedin"
    T3_DOCUMENT = "t3_document"
    T4_PAYROLL = "t4_payroll"
    T_RECEIPT = "t_receipt"  # for shopping reviews
    T_FRAUD_EVIDENCE = "t_fraud_evidence"  # for scam reports


class ReviewType(str, Enum):
    EMPLOYMENT = "employment"
    SHOPPING = "shopping"
    SCAM_REPORT = "scam_report"


class CompanyKind(str, Enum):
    EMPLOYER = "employer"
    MERCHANT = "merchant"
    BOTH = "both"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    handle: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    trust_score: float = 0.5
    verification_tier: VerificationTier = VerificationTier.NONE
    is_banned: bool = False


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    kind: CompanyKind = Field(default=CompanyKind.BOTH, index=True)
    domain: Optional[str] = Field(default=None, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Scam reputation
    is_scam_flagged: bool = Field(default=False, index=True)
    scam_reports_count: int = 0
    scam_severity: float = 0.0  # 0..1 aggregate severity
    last_scam_report_at: Optional[datetime] = None
    # Auto-flag only triggers after this many independent verified reports.
    # Until then the company shows "pending review" — never a public "scam" verdict.
    flag_review_threshold: int = 3


class EmploymentProof(SQLModel, table=True):
    __tablename__ = "employment_proofs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    company_id: UUID = Field(foreign_key="companies.id", index=True)
    tier: VerificationTier
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    artifact_ref: Optional[str] = None
    expires_at: Optional[datetime] = None


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: UUID = Field(foreign_key="companies.id", index=True)
    author_id: Optional[UUID] = Field(default=None, foreign_key="users.id", index=True)
    review_type: ReviewType = Field(default=ReviewType.EMPLOYMENT, index=True)

    title: str
    body: str

    # Employment-specific
    department: Optional[str] = None
    location: Optional[str] = None
    job_level: Optional[str] = None
    employment_status: Optional[str] = None

    # Shopping-specific
    product_or_service: Optional[str] = None
    purchase_amount: Optional[float] = None
    purchase_date: Optional[datetime] = None

    # Scam-report-specific
    scam_category: Optional[str] = None  # e.g. "fake_product", "non_delivery", "phishing"
    money_lost: Optional[float] = None

    # Universal ratings (1..5)
    rating_overall: float
    rating_culture: Optional[float] = None
    rating_management: Optional[float] = None
    rating_balance: Optional[float] = None
    rating_growth: Optional[float] = None
    rating_pay: Optional[float] = None
    rating_value: Optional[float] = None
    rating_shipping: Optional[float] = None
    rating_quality: Optional[float] = None
    rating_support: Optional[float] = None

    is_published: bool = True
    is_demo: bool = Field(default=False, index=True)
    submitter_ip_hash: Optional[str] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sentiment_score: Optional[float] = None
    fake_probability: Optional[float] = None


class EmailVerification(SQLModel, table=True):
    """One-time-password records for the T1 work-email verification flow.

    Tokens are short-lived (10 minutes). We never store the raw email or OTP —
    only salted SHA-256 hashes — so a database leak can't reveal contact info
    or be replayed by an attacker.
    """
    __tablename__ = "email_verifications"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    token: str = Field(unique=True, index=True)
    email_hash: str = Field(index=True)
    domain: str
    company_slug: Optional[str] = Field(default=None, index=True)
    otp_hash: str
    expires_at: datetime
    consumed_at: Optional[datetime] = None
    attempts: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ModerationAction(str, Enum):
    REMOVED = "removed"
    EDITED = "edited"
    WARNED = "warned"
    REINSTATED = "reinstated"


class ModerationLog(SQLModel, table=True):
    __tablename__ = "moderation_log"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    review_id: Optional[UUID] = Field(default=None, foreign_key="reviews.id", index=True)
    action: ModerationAction
    reason: str
    moderator_handle: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
