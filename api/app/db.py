from sqlmodel import SQLModel, Session, create_engine
from .config import get_settings

settings = get_settings()


def _normalize_db_url(url: str) -> str:
    # Railway uses postgres://; SQLAlchemy expects postgresql://. We also pin
    # the psycopg (v3) dialect since we ship psycopg[binary], not psycopg2.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine = create_engine(_normalize_db_url(settings.database_url), echo=False, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
