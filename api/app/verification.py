"""Signed, short-lived tokens that carry an email-verification result from
``POST /verify/email/confirm`` to ``POST /reviews`` so a freshly-submitted
review can be attributed to a verified author — making the T1 "verified work
email" badge actually reachable (previously the confirm step returned a
meaningless flag and every real review stayed ``verification_tier = none``).

Stateless and self-expiring (HS256 over the existing ``jwt_secret`` via
python-jose — the dependency that was declared but unused). No new table; the
token is opaque to the client and only meaningful to this server. Bound to the
verified email hash + company so a token minted for one company can't be
replayed to badge a review of a different company.
"""
import calendar
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from .config import get_settings

_ALGO = "HS256"
_PURPOSE = "review_verification"
_TTL_MINUTES = 30


def _epoch(dt: datetime) -> int:
    # utcnow() is naive UTC; timegm interprets the struct as UTC. (python-jose
    # expects numeric exp/iat, not datetimes.)
    return calendar.timegm(dt.utctimetuple())


def issue_review_verification_token(
    email_hash: str, domain: str, company_slug: Optional[str]
) -> str:
    """Mint a 30-minute token attesting a confirmed work-email verification."""
    now = datetime.utcnow()
    claims = {
        "purpose": _PURPOSE,
        "tier": "t1_email",
        "email_hash": email_hash,
        "domain": domain,
        "company_slug": company_slug,
        "iat": _epoch(now),
        "exp": _epoch(now + timedelta(minutes=_TTL_MINUTES)),
    }
    return jwt.encode(claims, get_settings().jwt_secret, algorithm=_ALGO)


def verify_review_verification_token(token: Optional[str]) -> Optional[dict]:
    """Return the decoded claims for a valid, unexpired, correct-purpose token,
    else None. Never raises — callers treat None as "not verified"."""
    if not token:
        return None
    try:
        claims = jwt.decode(token, get_settings().jwt_secret, algorithms=[_ALGO])
    except JWTError:
        return None
    if claims.get("purpose") != _PURPOSE:
        return None
    return claims
