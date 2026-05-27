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

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

# All publicly-listed companies (have a stock exchange listing) with an
# English label. Returns ~10-15k entries globally (NYSE, NASDAQ, LSE, TSX,
# TSE, DAX, FTSE, ASX, Euronext, BSE, JSE, …). License: CC0 / public domain.
WIKIDATA_QUERY = """
SELECT DISTINCT ?company ?companyLabel ?websiteUrl ?countryLabel WHERE {
  ?company wdt:P414 ?exchange .
  ?company rdfs:label ?en .
  FILTER(LANG(?en) = "en")
  OPTIONAL { ?company wdt:P856 ?websiteUrl. }
  OPTIONAL { ?company wdt:P17 ?country. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 15000
"""


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


def _extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    m = re.match(r"^https?://([^/]+)", url.strip())
    if not m:
        return None
    domain = m.group(1).lower()
    if domain.startswith("www."):
        domain = domain[4:]
    if not re.fullmatch(r"[a-z0-9.-]{3,253}", domain):
        return None
    return domain


def bulk_import_wikidata(session: Session, *, max_companies: int | None = None,
                        batch_size: int = 200) -> dict:
    """Import publicly-listed companies from Wikidata's SPARQL endpoint.

    Each Wikidata entity is filtered to those with a stock-exchange listing
    AND an English-language label, which keeps the import to notable named
    entities. The query is public-domain CC0 data.

    Each imported Company:
      - slug:        slugified label
      - name:        Wikidata label
      - kind:        BOTH
      - domain:      extracted from Wikidata's official-website property
      - description: "Publicly-listed company on {country}'s exchange."
    """
    log.info("Querying Wikidata SPARQL for publicly-listed companies")
    try:
        with httpx.Client(timeout=90) as client:
            r = client.get(
                WIKIDATA_SPARQL_URL,
                params={"query": WIKIDATA_QUERY, "format": "json"},
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/sparql-results+json",
                },
            )
        r.raise_for_status()
        bindings = r.json().get("results", {}).get("bindings", [])
    except Exception as e:
        log.warning("Wikidata fetch failed: %s", e)
        return {"added": 0, "skipped": 0, "error": str(e)[:200]}

    existing_slugs = set(session.exec(select(Company.slug)).all())

    candidate_rows: list[dict] = []
    seen_slugs_this_run: set[str] = set()
    skipped = 0

    for b in bindings:
        if max_companies is not None and len(candidate_rows) >= max_companies:
            break
        label = (b.get("companyLabel", {}).get("value") or "").strip()
        # Skip when SPARQL falls back to "Q12345" (no English label found)
        if not label or label.startswith("Q") and label[1:].isdigit():
            skipped += 1
            continue
        if _is_index_or_etf(label):
            skipped += 1
            continue
        slug = _slugify(label)
        if not slug or slug in existing_slugs or slug in seen_slugs_this_run:
            skipped += 1
            continue
        seen_slugs_this_run.add(slug)

        website = b.get("websiteUrl", {}).get("value")
        domain = _extract_domain(website)
        country = (b.get("countryLabel", {}).get("value") or "").strip()

        candidate_rows.append({
            "slug": slug,
            "name": label,
            "domain": domain,
            "country": country,
        })

    for i in range(0, len(candidate_rows), batch_size):
        chunk = candidate_rows[i:i + batch_size]
        for entry in chunk:
            desc = "Publicly-listed company."
            if entry["country"]:
                desc = f"Publicly-listed company in {entry['country']}."
            company = Company(
                slug=entry["slug"],
                name=entry["name"],
                kind=CompanyKind.BOTH,
                domain=entry["domain"],
                description=desc,
            )
            session.add(company)
        session.commit()
        log.info("Wikidata bulk-import progress: %d added", i + len(chunk))

    return {"added": len(candidate_rows), "skipped": skipped}


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

    # session.exec(select(scalar_column)) yields plain values in SQLModel,
    # NOT tuples — so we iterate directly. The previous (s,) destructuring
    # threw "too many values to unpack" and aborted the import silently.
    existing_slugs = set(session.exec(select(Company.slug)).all())

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
