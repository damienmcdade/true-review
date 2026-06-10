from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# Use typing.Optional rather than the PEP 604 `str | None` form: pydantic
# resolves these annotations at runtime (get_type_hints), so the union syntax
# would raise TypeError at import on Python < 3.10 — crashing the app before
# uvicorn binds and failing the platform healthcheck. Optional[...] is
# version-agnostic. (Python is also pinned to 3.11 via api/.python-version.)
class Settings(BaseSettings):
    database_url: str = "sqlite:///./local.db"
    jwt_secret: str = "dev-secret-change-me"
    cors_origins: str = "http://localhost:3000"
    anthropic_api_key: Optional[str] = None
    ai_gateway_url: Optional[str] = None
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
