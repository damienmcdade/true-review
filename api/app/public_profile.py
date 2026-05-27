"""Public-profile synthesis from license-clean sources.

For every company in the catalog — even the ~24k EDGAR/Wikidata/MediaWiki
entries without any reviews yet — we can compose a factual page from:

  - Wikipedia REST API (real article extract, CC-BY-SA attributed)
  - SEC EDGAR submissions data (ticker, CIK, recent filings, SIC sector)
  - Groq llama-3.3-70b synthesis: one paragraph of neutral facts derived
    only from the above. Clearly labeled as AI synthesis, distinct from
    user reviews.

The synthesized paragraph is intentionally fact-only, no workplace
opinions / no review-style language — to keep this distinct from
the user-reviews surface and to avoid any defamation exposure.
"""
from __future__ import annotations

import os
from typing import Optional

import httpx

from .ai import GROQ_URL, GROQ_MODEL_DEFAULT
from .enrichment import fetch_wikipedia_summary, fetch_edgar


_SYSTEM_PROMPT = (
    "You are a neutral factual summariser. You write a single short paragraph "
    "(3-5 sentences) describing what is PUBLICLY KNOWN about a company, "
    "based ONLY on the sources the user provides. Strict rules:\n"
    "1. State concrete facts: industry, country, ownership status, scale, "
    "founding date if present, listing status if public.\n"
    "2. Do NOT speculate about workplace experience, culture, leadership "
    "quality, or anything review-like.\n"
    "3. Do NOT include opinions or subjective phrasing.\n"
    "4. If both sources are empty or unhelpful, reply exactly: "
    "'No public sources available for this company yet.'\n"
    "5. End with the sentence: 'Sources: <comma-separated list>.'"
)


async def build_public_profile(company_name: str, *, timeout_s: float = 18.0) -> dict:
    """Compose a public profile from Wikipedia + SEC EDGAR + Groq."""
    wiki = await fetch_wikipedia_summary(company_name)
    edgar = await fetch_edgar(company_name)

    have_wiki = bool(wiki.get("found"))
    have_edgar = bool(edgar.get("found"))
    sources: list[str] = []
    if have_wiki:
        sources.append("Wikipedia")
    if have_edgar:
        sources.append("SEC EDGAR")

    ai_synthesis: Optional[str] = None
    ai_model: Optional[str] = None

    api_key = os.environ.get("GROQ_API_KEY")
    if api_key and (have_wiki or have_edgar):
        context_chunks: list[str] = []
        if have_wiki:
            extract = (wiki.get("extract") or "").strip()
            context_chunks.append(
                f"Wikipedia (CC-BY-SA): {extract[:1800]}"
            )
        if have_edgar:
            ticker = edgar.get("ticker")
            cik = edgar.get("cik")
            sic = edgar.get("sic") or "n/a"
            recent = edgar.get("recent_filings") or []
            forms = ", ".join(f.get("form", "") for f in recent[:3] if f.get("form"))
            context_chunks.append(
                f"SEC EDGAR: US-public-filer. Ticker {ticker}. CIK {cik}. "
                f"Industry classification (SIC): {sic}. "
                f"Recent filings on record: {forms or 'n/a'}."
            )
        prompt = (
            f"Company: {company_name}\n\n"
            f"Sources (use only these — invent nothing):\n"
            + "\n\n".join(context_chunks)
        )

        try:
            async with httpx.AsyncClient(timeout=timeout_s) as client:
                resp = await client.post(
                    GROQ_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": GROQ_MODEL_DEFAULT,
                        "temperature": 0.1,
                        "max_tokens": 300,
                        "messages": [
                            {"role": "system", "content": _SYSTEM_PROMPT},
                            {"role": "user", "content": prompt},
                        ],
                    },
                )
            if resp.status_code < 400:
                ai_synthesis = resp.json()["choices"][0]["message"]["content"].strip()
                ai_model = GROQ_MODEL_DEFAULT
        except Exception:
            ai_synthesis = None

    return {
        "company_name": company_name,
        "ai_synthesis": ai_synthesis,
        "ai_model": ai_model,
        "wikipedia": wiki if have_wiki else None,
        "edgar": edgar if have_edgar else None,
        "sources": sources,
    }
