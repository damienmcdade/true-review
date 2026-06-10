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


def _assert_secure_config() -> None:
    """Production safety gate, run at import.

    FAIL-FAST if JWT_SECRET is still the public in-repo default in production:
    verification tokens are HS256-signed with it, so a default would let anyone
    forge a 't1_email' "verified employee" badge with no email at all. Better to
    refuse to boot than to serve forgeable trust badges.

    WARN (non-fatal) on default IP/OTP hash salts — those protect lower-value,
    short-lived data, and failing closed there would needlessly crash a deploy
    that simply hasn't set them yet. Set IP_HASH_SALT / VERIFY_HASH_SALT to
    silence the warning.
    """
    import os
    import sys

    s = get_settings()
    if not s.database_url.startswith(("postgres://", "postgresql://")):
        return  # local/dev (SQLite) — defaults are fine
    if s.jwt_secret == "dev-secret-change-me":
        raise RuntimeError(
            "JWT_SECRET is the public in-repo default in a production deployment "
            "— verification badge tokens would be forgeable. Set JWT_SECRET to a "
            "strong random value before deploying."
        )
    weak = [
        name
        for name, default in (
            ("IP_HASH_SALT", "true-review-default-salt-rotate-me"),
            ("VERIFY_HASH_SALT", "true-review-verify-salt-rotate-me"),
        )
        if os.environ.get(name, default) == default
    ]
    if weak:
        print(
            f"[config] WARNING: default hash salt(s) in production: {', '.join(weak)}. "
            "Set them to strong random values.",
            file=sys.stderr,
        )


_assert_secure_config()
