"""Security utilities: content sanitization, IP hashing, prompt-injection
mitigation, and basic content filters.
"""
from __future__ import annotations

import hashlib
import os
import re
from typing import Optional


# Regex of obvious PII patterns we refuse to publish.
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
PHONE_RE = re.compile(r"\b\d{3}[\s.-]?\d{3}[\s.-]?\d{4}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
CREDIT_CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")

# Block obviously identifying claims about individuals by name + role.
NAMED_INDIVIDUAL_HINT = re.compile(
    r"\b(CEO|CFO|CTO|COO|VP|director|manager|founder)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b"
)


def hash_ip(ip: Optional[str]) -> Optional[str]:
    """One-way IP hash for rate limiting + abuse correlation.
    Stored separately from review content; we never log raw IPs.
    """
    if not ip:
        return None
    salt = os.environ.get("IP_HASH_SALT", "true-review-default-salt-rotate-me")
    return hashlib.sha256(f"{salt}::{ip}".encode()).hexdigest()[:32]


def sanitize_text(s: str, *, max_len: int = 5000) -> str:
    """Strip control chars and clamp length. Does not touch HTML — we never
    render user content as HTML; all output is React text nodes."""
    if not s:
        return ""
    # Remove NUL + other C0 control chars except \n and \t.
    cleaned = "".join(ch for ch in s if ch in ("\n", "\t") or 32 <= ord(ch) < 127 or ord(ch) > 159)
    cleaned = cleaned.strip()
    return cleaned[:max_len]


def detect_problems(s: str) -> list[str]:
    """Return a list of problem codes if the content should be rejected
    or queued for moderation. Empty list = safe to publish."""
    problems: list[str] = []
    if SSN_RE.search(s):
        problems.append("contains_ssn")
    if CREDIT_CARD_RE.search(s):
        problems.append("contains_card_number")
    if EMAIL_RE.search(s):
        problems.append("contains_email_address")
    if PHONE_RE.search(s):
        problems.append("contains_phone_number")
    if NAMED_INDIVIDUAL_HINT.search(s):
        problems.append("identifies_named_individual")
    return problems


_INJECTION_PATTERNS = [
    # Direct override attempts
    r"ignore (all |any )?(previous|prior|above|earlier) (instructions?|prompts?|rules?)",
    r"disregard (all |any |the )?(previous|prior|above|earlier)",
    r"forget (everything|all) (above|before|prior)",
    r"override (your|the|all) (instructions?|rules?|system)",
    # Persona switches
    r"you (are|will be) (now |a |an )?(?:pirate|cat|dog|child|hacker|admin|developer|jailbroken)",
    r"act (as|like) (a |an )?(?:pirate|cat|dog|hacker|admin|developer)",
    r"pretend (to be|you are|you're)",
    r"roleplay (as|the)",
    r"speak (like|as) (a |an )",
    # Direct instructions
    r"new instructions?:",
    r"system prompt[: ]",
    r"(your|the) (new|real|actual|true) (instructions?|task|goal|prompt)",
    # Output-format hijacks
    r"output (only|just) ['\"]",
    r"respond (only |just )?with ['\"]",
]
_INJECTION_RE = re.compile("|".join(f"(?:{p})" for p in _INJECTION_PATTERNS), re.IGNORECASE)


def harden_prompt_input(s: str, *, max_len: int = 4000) -> str:
    """Mitigate prompt injection from user-controlled text fed to the LLM.

    - Truncate.
    - Strip lines that look like 'system:' / 'assistant:' role markers.
    - Replace known injection patterns with a noise token so the LLM still
      sees the surrounding context but the imperative is broken.
    - Wrap content in clear delimiters in the calling caller (not here).
    """
    if not s:
        return ""
    s = s[:max_len]
    # Strip lines that try to impersonate a role
    s = re.sub(
        r"(?im)^\s*(system|assistant|user|developer|tool)\s*:\s*",
        "",
        s,
    )
    s = _INJECTION_RE.sub("[redacted-injection]", s)
    return s


def is_rate_limit_key_from_request(request) -> str:
    """Build a rate-limit key. Falls back to a constant if no IP — never
    bypasses the limit silently."""
    try:
        fwd = request.headers.get("x-forwarded-for", "")
        ip = fwd.split(",")[0].strip() if fwd else request.client.host
    except Exception:
        ip = "unknown"
    return ip or "unknown"
