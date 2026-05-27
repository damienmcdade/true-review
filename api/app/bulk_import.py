"""Large-scale company import from public registries.

EDGAR: SEC's full ticker → CIK → title map, covering every US publicly-
traded company (~10k entries). License: public domain. No auth required.
Their request guidance is to identify yourself with a User-Agent.

Idempotent — skips slugs that already exist. Safe to re-run.

Reviews are NOT created for imported companies. They land in the catalog
empty, and become populated as real verified users post. Search /
discover / scam-check all still work on them. Wikipedia + EDGAR
enrichment fills in real metadata on the company page.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Iterable

import httpx
from sqlmodel import Session, select

from .models import Company, CompanyKind


log = logging.getLogger("true_review.bulk_import")

USER_AGENT = (
    "TrueReview/0.5 (https://truereview.dev; legal@truereview.dev)"
)

EDGAR_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return s[:200] or ""


def _is_index_or_etf(name: str) -> bool:
    """Skip ETFs, mutual funds, trusts, and similar non-operating entities.
    They appear in the SEC ticker list but aren't useful as "companies"
    in a workplace-and-shopping review context."""
    n = name.lower()
    keywords = (
        " etf",
        " fund",
        " trust",
        " spdr",
        " ishares",
        " invesco",
        "exchange-traded",
        " etn ",
        " preferred",
        " warrant",
        " unit ",
        " bond ",
        " note ",
        " convertible",
        "common stock",
        "ordinary shares",
        " plc ",
    )
    return any(k in n for k in keywords)


def _fetch_edgar_tickers() -> list[dict]:
    log.info("Fetching SEC EDGAR ticker list")
    with httpx.Client(timeout=30) as client:
        r = client.get(EDGAR_TICKERS_URL, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    raw = r.json()
    # raw shape: {"0":{"cik_str":320193,"ticker":"AAPL","title":"Apple Inc."}, ...}
    return list(raw.values())


def bulk_import_edgar(session: Session, *, max_companies: int | None = None,
                     batch_size: int = 200) -> dict:
    """Import EDGAR's full company list. Returns {added, skipped}.

    Each imported Company:
      - slug:        slugified title
      - name:        title
      - kind:        BOTH (could be employer + merchant)
      - description: "Public company. Ticker: X. SEC CIK: 000123"
    """
    try:
        rows = _fetch_edgar_tickers()
    except Exception as e:
        log.warning("EDGAR ticker fetch failed: %s", e)
        return {"added": 0, "skipped": 0, "error": str(e)[:200]}

    existing_slugs = {
        s for (s,) in session.exec(select(Company.slug)).all()
    }

    added = 0
    skipped = 0
    candidate_rows: list[dict] = []
    for row in rows:
        if max_companies is not None and added + len(candidate_rows) >= max_companies:
            break
        title = (row.get("title") or "").strip()
        ticker = (row.get("ticker") or "").strip()
        cik = row.get("cik_str")
        if not title or not ticker or cik is None:
            skipped += 1
            continue
        if _is_index_or_etf(title):
            skipped += 1
            continue
        slug = _slugify(title)
        if not slug or slug in existing_slugs:
            skipped += 1
            continue
        existing_slugs.add(slug)  # avoid duplicates within this batch too
        candidate_rows.append({
            "slug": slug,
            "name": title,
            "ticker": ticker,
            "cik": f"{int(cik):010d}",
        })

    # Insert in batches to keep transactions small.
    for i in range(0, len(candidate_rows), batch_size):
        chunk = candidate_rows[i:i + batch_size]
        for entry in chunk:
            company = Company(
                slug=entry["slug"],
                name=entry["name"],
                kind=CompanyKind.BOTH,
                domain=None,
                description=(
                    f"Public company. Ticker: {entry['ticker']}. "
                    f"SEC CIK: {entry['cik']}."
                ),
            )
            session.add(company)
            added += 1
        session.commit()
        log.info("EDGAR bulk-import progress: %d added", added)

    return {"added": added, "skipped": skipped}
