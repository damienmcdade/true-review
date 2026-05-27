import logging

from sqlalchemy import inspect, text
from sqlmodel import SQLModel, Session, create_engine

from .config import get_settings

settings = get_settings()
log = logging.getLogger("true_review.db")


def _normalize_db_url(url: str) -> str:
    # Railway uses postgres://; SQLAlchemy expects postgresql://. We also pin
    # the psycopg (v3) dialect since we ship psycopg[binary], not psycopg2.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(_normalize_db_url(settings.database_url), echo=False, pool_pre_ping=True)


# Columns we expect on `companies` after the v0.3 schema change. If any of
# these are missing from an existing table, we know we're on an older
# pre-migration schema and need to recreate.
_REQUIRED_COMPANY_COLUMNS = {
    "kind",
    "is_scam_flagged",
    "scam_reports_count",
    "scam_severity",
    "last_scam_report_at",
    "flag_review_threshold",
}

# Columns we expect on `reviews` after the v0.3 schema change.
_REQUIRED_REVIEW_COLUMNS = {
    "review_type",
    "product_or_service",
    "purchase_amount",
    "purchase_date",
    "scam_category",
    "money_lost",
    "is_demo",
    "submitter_ip_hash",
}


def _schema_is_out_of_sync(insp) -> bool:
    """True if existing tables exist but are missing v0.3+ columns/tables."""
    tables = set(insp.get_table_names())
    if "companies" in tables:
        existing = {c["name"] for c in insp.get_columns("companies")}
        if not _REQUIRED_COMPANY_COLUMNS.issubset(existing):
            return True
    if "reviews" in tables:
        existing = {c["name"] for c in insp.get_columns("reviews")}
        if not _REQUIRED_REVIEW_COLUMNS.issubset(existing):
            return True
    # v0.4: email_verifications table introduced. If users/companies exist
    # without it, recreate so the new feature works.
    if tables and "users" in tables and "email_verifications" not in tables:
        return True
    return False


def init_db() -> None:
    """Create tables. If we detect a pre-v0.3 schema, drop and recreate.

    This is safe right now because the database contains only seeded demo
    content — no real user reviews. Once we have real users, swap this for
    an Alembic migration.
    """
    insp = inspect(engine)
    if _schema_is_out_of_sync(insp):
        log.warning("Pre-v0.3 schema detected on existing tables. Dropping and recreating.")
        with engine.begin() as conn:
            for tbl in ("security_events", "moderation_log", "employment_proofs",
                        "email_verifications", "reviews", "users", "companies"):
                conn.execute(text(f'DROP TABLE IF EXISTS "{tbl}" CASCADE'))
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
