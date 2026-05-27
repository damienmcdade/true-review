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


# SQLAlchemy stores Python Enum *member names* (uppercase) in the Postgres
# enum type, not the .value strings. So the Pg enum's labels are NONE,
# T1_EMAIL, T2_LINKEDIN, T3_DOCUMENT, T4_PAYROLL, T_RECEIPT, T_FRAUD_EVIDENCE.
_REQUIRED_VERIFICATIONTIER_VALUES = {
    "NONE",
    "T1_EMAIL",
    "T2_LINKEDIN",
    "T3_DOCUMENT",
    "T4_PAYROLL",
    "T_RECEIPT",         # added v0.4 for shopping reviews
    "T_FRAUD_EVIDENCE",  # added v0.4 for scam reports
}


def _enum_values(conn, type_name: str) -> set[str]:
    rows = conn.execute(
        text(
            "SELECT e.enumlabel FROM pg_type t "
            "JOIN pg_enum e ON e.enumtypid = t.oid "
            "WHERE t.typname = :name"
        ),
        {"name": type_name},
    ).fetchall()
    return {r[0] for r in rows}


def _schema_is_out_of_sync(insp) -> bool:
    """True if existing tables exist but are missing v0.3+ columns/tables/enum values."""
    tables = set(insp.get_table_names())
    if "companies" in tables:
        existing = {c["name"] for c in insp.get_columns("companies")}
        if not _REQUIRED_COMPANY_COLUMNS.issubset(existing):
            return True
    if "reviews" in tables:
        existing = {c["name"] for c in insp.get_columns("reviews")}
        if not _REQUIRED_REVIEW_COLUMNS.issubset(existing):
            return True
    if tables and "users" in tables and "email_verifications" not in tables:
        return True
    # Enum drift — if the Postgres enum is missing v0.4 verifier tiers, recreate.
    if tables and "users" in tables:
        try:
            with engine.connect() as conn:
                vals = _enum_values(conn, "verificationtier")
            if vals and not _REQUIRED_VERIFICATIONTIER_VALUES.issubset(vals):
                return True
        except Exception:
            pass
    return False


def init_db() -> None:
    """Create tables. If we detect a pre-v0.3 schema, drop and recreate.

    This is safe right now because the database contains only seeded demo
    content — no real user reviews. Once we have real users, swap this for
    an Alembic migration.

    Additionally: non-destructively ADD any missing values to the
    verificationtier Postgres enum. New tier values added in Python (e.g.
    t_receipt, t_fraud_evidence) need to be reflected on the live enum.
    Postgres requires ALTER TYPE ... ADD VALUE to be run *outside* a
    transaction, so each ADD VALUE is committed individually.
    """
    insp = inspect(engine)
    if _schema_is_out_of_sync(insp):
        log.warning("Out-of-sync schema detected. Dropping tables + enum types and recreating.")
        with engine.begin() as conn:
            for tbl in ("security_events", "moderation_log", "employment_proofs",
                        "email_verifications", "reviews", "users", "companies"):
                conn.execute(text(f'DROP TABLE IF EXISTS "{tbl}" CASCADE'))
            for typ in ("verificationtier", "companykind", "reviewtype", "moderationaction"):
                conn.execute(text(f'DROP TYPE IF EXISTS "{typ}" CASCADE'))

    SQLModel.metadata.create_all(engine)

    # Idempotent enum top-up for upgrades that didn't trigger a full recreate.
    try:
        with engine.connect() as conn:
            existing = _enum_values(conn, "verificationtier")
        for val in _REQUIRED_VERIFICATIONTIER_VALUES - existing:
            with engine.connect() as conn:
                conn.execution_options(isolation_level="AUTOCOMMIT").execute(
                    text(f"ALTER TYPE verificationtier ADD VALUE IF NOT EXISTS '{val}'")
                )
                log.info("Added enum value verificationtier.%s", val)
    except Exception as e:  # noqa: BLE001
        # If the enum doesn't exist yet (SQLite local dev, or fresh DB), skip.
        log.info("Skipping enum top-up: %s", e)


def get_session():
    with Session(engine) as session:
        yield session
