from sqlmodel import SQLModel, Session, create_engine
from .config import get_settings

settings = get_settings()

# Railway provides DATABASE_URL with postgres:// — SQLAlchemy wants postgresql://
db_url = settings.database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url, echo=False, pool_pre_ping=True)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
