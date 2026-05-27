"""Email delivery via Resend (free tier 100/day).

Set RESEND_API_KEY + RESEND_FROM in env. Without them we fall back to
logging the OTP to stdout so the flow still works in dev — never expose
the dev log to the public verifier UI.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

import httpx

log = logging.getLogger("true_review.email")


async def send_otp(to_email: str, otp: str, company_name: Optional[str] = None) -> dict:
    """Send a 6-digit OTP. Returns {sent: bool, channel: 'resend'|'log', error?: ...}."""
    api_key = os.environ.get("RESEND_API_KEY")
    sender = os.environ.get("RESEND_FROM", "True Review <onboarding@resend.dev>")

    subject = "Your True Review verification code"
    text = (
        f"Your True Review code is: {otp}\n\n"
        f"It expires in 10 minutes. If you didn't request this, ignore the email.\n"
        + (f"\nCompany being verified: {company_name}\n" if company_name else "")
    )
    html = (
        f"<p>Your True Review verification code is</p>"
        f"<p style='font-size:28px;letter-spacing:6px;font-weight:600'>{otp}</p>"
        f"<p>It expires in 10 minutes. If you didn't request this, ignore this email.</p>"
        + (f"<p>Company being verified: <strong>{company_name}</strong></p>" if company_name else "")
    )

    if not api_key:
        # Dev fallback: log so a human running the API locally can complete the flow.
        # Production deployments MUST set RESEND_API_KEY before launch.
        log.warning("RESEND_API_KEY not set; OTP for %s = %s (dev log only)", to_email, otp)
        return {"sent": False, "channel": "log", "error": "RESEND_API_KEY missing"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": sender,
                    "to": [to_email],
                    "subject": subject,
                    "html": html,
                    "text": text,
                },
            )
        if r.status_code >= 400:
            return {"sent": False, "channel": "resend", "error": r.text[:200]}
        return {"sent": True, "channel": "resend", "id": r.json().get("id")}
    except Exception as e:  # noqa: BLE001
        return {"sent": False, "channel": "resend", "error": str(e)[:200]}
