from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship


class VerificationTier(str, Enum):
    NONE = "none"
    T1_EMAIL = "t1_email"
    T2_LINKEDIN = "t2_linkedin"
    T3_DOCUMENT = "t3_document"
    T4_PAYROLL = "t4_payroll"


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
    domain: Optional[str] = Field(default=None, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EmploymentProof(SQLModel, table=True):
    __tablename__ = "employment_proofs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    company_id: UUID = Field(foreign_key="companies.id", index=True)
    tier: VerificationTier
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    # Encrypted proof artifact reference (never returned to clients)
    artifact_ref: Optional[str] = None
    expires_at: Optional[datetime] = None


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: UUID = Field(foreign_key="companies.id", index=True)
    author_id: UUID = Field(foreign_key="users.id", index=True)
    title: str
    body: str
    department: Optional[str] = None
    location: Optional[str] = None
    job_level: Optional[str] = None
    employment_status: Optional[str] = None  # current / former
    rating_overall: float
    rating_culture: float
    rating_management: float
    rating_balance: float
    rating_growth: float
    rating_pay: float
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # AI-derived
    sentiment_score: Optional[float] = None
    fake_probability: Optional[float] = None


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
