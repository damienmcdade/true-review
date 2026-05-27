"""External real-data enrichment from license-clean public sources.

Sources used:
- Wikipedia REST API           — free, no auth, public domain.
- OpenCorporates v0.4          — free tier, no auth, rate-limited.
- SEC EDGAR full-text search   — free, no auth, requires User-Agent header.
- URLhaus (abuse.ch) v1        — free, requires Auth-Key for registered users.

All fetchers are async + cached in memory for the process lifetime.
Failures degrade gracefully — callers get an empty/None payload, never a 5xx.
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

import httpx


USER_AGENT = (
    "TrueReview/0.4 (https://truereview.dev; legal@truereview.dev)"
)


@dataclass
class _CacheEntry:
    value: dict
    expires_at: float


_cache: dict[str, _CacheEntry] = {}


def _cached(key: str, ttl_seconds: int):
    entry = _cache.get(key)
    if entry and entry.expires_at > time.time():
        return entry.value
    return None


def _store(key: str, value: dict, ttl_seconds: int) -> None:
    _cache[key] = _CacheEntry(value=value, expires_at=time.time() + ttl_seconds)


# --------------------------------------------------------------------------- #
# Wikipedia
# --------------------------------------------------------------------------- #

async def fetch_wikipedia_summary(name: str) -> dict:
    """Returns {title, description, extract, url} or {error: ...}."""
    key = f"wiki:{name.lower()}"
    if (c := _cached(key, 3600)) is not None:
        return c
    safe = quote(name.strip().replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe}"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(url, headers={"User-Agent": USER_AGENT})
        if r.status_code == 404:
            out = {"found": False}
        elif r.status_code >= 400:
            out = {"found": False, "error": f"http_{r.status_code}"}
        else:
            d = r.json()
            out = {
                "found": True,
                "title": d.get("title"),
                "description": d.get("description"),
                "extract": d.get("extract"),
                "url": d.get("content_urls", {}).get("desktop", {}).get("page"),
                "thumbnail": (d.get("thumbnail") or {}).get("source"),
            }
    except Exception as e:  # noqa: BLE001
        out = {"found": False, "error": str(e)[:120]}
    _store(key, out, 3600)
    return out


# --------------------------------------------------------------------------- #
# OpenCorporates
# --------------------------------------------------------------------------- #

async def fetch_opencorporates(name: str) -> dict:
    """Returns top 5 matches with jurisdiction, status, registration number."""
    key = f"oc:{name.lower()}"
    if (c := _cached(key, 3600)) is not None:
        return c
    url = (
        "https://api.opencorporates.com/v0.4/companies/search"
        f"?q={quote(name)}&per_page=5"
    )
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers={"User-Agent": USER_AGENT})
        if r.status_code >= 400:
            out = {"found": False, "error": f"http_{r.status_code}"}
        else:
            d = r.json()
            companies = d.get("results", {}).get("companies", []) or []
            out = {
                "found": bool(companies),
                "matches": [
                    {
                        "name": (c.get("company") or {}).get("name"),
                        "jurisdiction": (c.get("company") or {}).get("jurisdiction_code"),
                        "number": (c.get("company") or {}).get("company_number"),
                        "status": (c.get("company") or {}).get("current_status"),
                        "opencorporates_url": (c.get("company") or {}).get("opencorporates_url"),
                    }
                    for c in companies
                ],
            }
    except Exception as e:  # noqa: BLE001
        out = {"found": False, "error": str(e)[:120]}
    _store(key, out, 3600)
    return out


# --------------------------------------------------------------------------- #
# SEC EDGAR
# --------------------------------------------------------------------------- #

_EDGAR_TICKER_CACHE: Optional[dict] = None


async def _load_edgar_tickers() -> dict:
    """Load the SEC's full ticker → CIK map once. Cached for the process."""
    global _EDGAR_TICKER_CACHE
    if _EDGAR_TICKER_CACHE is not None:
        return _EDGAR_TICKER_CACHE
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(
                "https://www.sec.gov/files/company_tickers.json",
                headers={"User-Agent": USER_AGENT},
            )
        if r.status_code >= 400:
            return {}
        raw = r.json()
        # Format: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
        index = {}
        for v in raw.values():
            index[v["title"].lower()] = {
                "cik": f"{v['cik_str']:010d}",
                "ticker": v["ticker"],
                "title": v["title"],
            }
        _EDGAR_TICKER_CACHE = index
        return index
    except Exception:
        return {}


async def fetch_edgar(name: str) -> dict:
    """Returns SEC info for a US public company matching name, if any."""
    key = f"edgar:{name.lower()}"
    if (c := _cached(key, 3600)) is not None:
        return c

    tickers = await _load_edgar_tickers()
    if not tickers:
        out = {"found": False, "error": "edgar_index_unavailable"}
        _store(key, out, 600)
        return out

    n = name.lower().strip()
    # Try exact-ish match, then prefix
    match = tickers.get(n)
    if not match:
        for title, info in tickers.items():
            if n in title or title in n:
                match = info
                break
    if not match:
        out = {"found": False}
        _store(key, out, 1800)
        return out

    cik = match["cik"]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"https://data.sec.gov/submissions/CIK{cik}.json",
                headers={"User-Agent": USER_AGENT},
            )
        if r.status_code >= 400:
            out = {"found": True, **match, "filings_error": f"http_{r.status_code}"}
        else:
            d = r.json()
            recent = d.get("filings", {}).get("recent", {}) or {}
            forms = recent.get("form", [])[:5]
            dates = recent.get("filingDate", [])[:5]
            accessions = recent.get("accessionNumber", [])[:5]
            primary_docs = recent.get("primaryDocument", [])[:5]
            out = {
                "found": True,
                "ticker": match["ticker"],
                "title": match["title"],
                "cik": cik,
                "sic": d.get("sicDescription"),
                "address": (d.get("addresses") or {}).get("business"),
                "recent_filings": [
                    {
                        "form": forms[i] if i < len(forms) else None,
                        "date": dates[i] if i < len(dates) else None,
                        "url": (
                            f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                            f"{accessions[i].replace('-', '')}/{primary_docs[i]}"
                            if i < len(accessions) and i < len(primary_docs)
                            else None
                        ),
                    }
                    for i in range(min(5, len(forms)))
                ],
            }
    except Exception as e:  # noqa: BLE001
        out = {"found": True, **match, "filings_error": str(e)[:120]}
    _store(key, out, 3600)
    return out


# --------------------------------------------------------------------------- #
# URLhaus (abuse.ch) — phishing / malware host check
# --------------------------------------------------------------------------- #

_DOMAIN_RE = re.compile(r"^[a-zA-Z0-9.-]{3,253}$")


async def fetch_urlhaus(domain: str) -> dict:
    """Check a domain against the URLhaus malicious-URL feed.

    Returns:
      {checked: bool, found: bool, listings?: [...], error?: str}

    Requires URLHAUS_AUTH_KEY in env. Free key at https://auth.abuse.ch.
    Without the key we return checked=False so callers can show a "not
    configured" hint instead of a misleading clean result.
    """
    if not domain or not _DOMAIN_RE.match(domain):
        return {"checked": False, "error": "invalid_domain"}

    key = f"urlhaus:{domain.lower()}"
    if (c := _cached(key, 600)) is not None:
        return c

    auth_key = os.environ.get("URLHAUS_AUTH_KEY")
    if not auth_key:
        out = {
            "checked": False,
            "error": "URLHAUS_AUTH_KEY not configured. Free key at https://auth.abuse.ch.",
        }
        _store(key, out, 60)
        return out

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.post(
                "https://urlhaus-api.abuse.ch/v1/host/",
                headers={"Auth-Key": auth_key, "User-Agent": USER_AGENT},
                data={"host": domain},
            )
        if r.status_code >= 400:
            out = {"checked": True, "found": False, "error": f"http_{r.status_code}"}
        else:
            d = r.json()
            status = d.get("query_status")
            if status == "ok":
                urls = (d.get("urls") or [])[:5]
                out = {
                    "checked": True,
                    "found": True,
                    "threat_count": d.get("url_count"),
                    "first_seen": d.get("firstseen"),
                    "listings": [
                        {
                            "url": u.get("url"),
                            "threat": u.get("threat"),
                            "tags": u.get("tags") or [],
                            "date_added": u.get("date_added"),
                        }
                        for u in urls
                    ],
                }
            elif status == "no_results":
                out = {"checked": True, "found": False}
            else:
                out = {"checked": True, "found": False, "status": status}
    except Exception as e:  # noqa: BLE001
        out = {"checked": True, "found": False, "error": str(e)[:120]}
    _store(key, out, 600)
    return out
