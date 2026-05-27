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

# Second Wikidata pass — notable PRIVATE companies (i.e. without a stock-
# exchange listing) that nonetheless have an English Wikipedia article.
# Using a fixed set of business-class types instead of P279* recursion so
# the query is fast enough for Wikidata's 60-second SPARQL timeout. Each
# class roughly maps to: business / company / private company / for-profit
# corporation / non-profit organisation / state-owned enterprise.
WIKIDATA_PRIVATE_QUERY = """
SELECT DISTINCT ?company ?companyLabel ?websiteUrl ?countryLabel WHERE {
  VALUES ?type { wd:Q4830453 wd:Q783794 wd:Q6881511 wd:Q270791 wd:Q163740 wd:Q5621421 }
  ?company wdt:P31 ?type .
  ?article schema:about ?company .
  ?article schema:isPartOf <https://en.wikipedia.org/> .
  FILTER NOT EXISTS { ?company wdt:P414 ?exchange. }
  OPTIONAL { ?company wdt:P856 ?websiteUrl. }
  OPTIONAL { ?company wdt:P17 ?country. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 20000
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


def _run_wikidata_query(query: str, label: str) -> list[dict]:
    """Run one SPARQL query; return the bindings list (empty on failure)."""
    log.info("Querying Wikidata SPARQL: %s", label)
    try:
        with httpx.Client(timeout=120) as client:
            r = client.get(
                WIKIDATA_SPARQL_URL,
                params={"query": query, "format": "json"},
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/sparql-results+json",
                },
            )
        r.raise_for_status()
        return r.json().get("results", {}).get("bindings", []) or []
    except Exception as e:
        log.warning("Wikidata fetch failed (%s): %s", label, e)
        return []


def bulk_import_wikidata(session: Session, *, max_companies: int | None = None,
                        batch_size: int = 200,
                        include_private: bool = True) -> dict:
    """Import companies from Wikidata's SPARQL endpoint.

    Stage A — publicly-listed companies (have P414 stock-exchange listing).
              Covers every global public market with an English label.
    Stage B — private companies (no P414) that have an English Wikipedia
              article. Covers Cargill, IKEA Group, SpaceX-pre-IPO, Mars,
              Aldi Group, Bosch, Bloomberg, Bechtel, etc. — privately-held
              majors people search for. Skipped if include_private=False.

    Each Wikidata entity is the public-domain (CC0) Wikidata record.

    Each imported Company:
      - slug:        slugified label
      - name:        Wikidata label
      - kind:        BOTH
      - domain:      extracted from Wikidata's official-website property
      - description: "Publicly-listed company in {country}." OR
                     "Private/notable company in {country}."
    """
    listed_bindings = _run_wikidata_query(WIKIDATA_QUERY, "publicly-listed")
    private_bindings = (
        _run_wikidata_query(WIKIDATA_PRIVATE_QUERY, "private + notable")
        if include_private else []
    )

    if not listed_bindings and not private_bindings:
        return {"added": 0, "skipped": 0, "error": "both Wikidata queries returned empty"}

    existing_slugs = set(session.exec(select(Company.slug)).all())

    candidate_rows: list[dict] = []
    seen_slugs_this_run: set[str] = set()
    skipped = 0

    def harvest(bindings: list[dict], is_listed: bool) -> None:
        nonlocal skipped
        for b in bindings:
            if max_companies is not None and len(candidate_rows) >= max_companies:
                return
            label = (b.get("companyLabel", {}).get("value") or "").strip()
            if not label or (label.startswith("Q") and label[1:].isdigit()):
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
                "listed": is_listed,
            })

    harvest(listed_bindings, is_listed=True)
    harvest(private_bindings, is_listed=False)

    for i in range(0, len(candidate_rows), batch_size):
        chunk = candidate_rows[i:i + batch_size]
        for entry in chunk:
            if entry["listed"]:
                desc = "Publicly-listed company."
                if entry["country"]:
                    desc = f"Publicly-listed company in {entry['country']}."
            else:
                desc = "Privately-held / notable company."
                if entry["country"]:
                    desc = f"Privately-held / notable company in {entry['country']}."
            company = Company(
                slug=entry["slug"],
                name=entry["name"],
                kind=CompanyKind.BOTH,
                domain=entry["domain"],
                description=desc,
            )
            session.add(company)
        session.commit()
        log.info("Wikidata bulk-import progress: %d added (running total)",
                 i + len(chunk))

    return {
        "added": len(candidate_rows),
        "skipped": skipped,
        "listed_returned": len(listed_bindings),
        "private_returned": len(private_bindings),
    }


MEDIAWIKI_API = "https://en.wikipedia.org/w/api.php"

# Wikipedia categories of notable companies. MediaWiki's list=categorymembers
# is a different endpoint than WDQS SPARQL and is not affected by WDQS
# outages. Each category typically returns 200-500 well-curated entries.
# Public-domain (CC-BY-SA category structure; titles are factual data).
MEDIAWIKI_CATEGORIES = [
    "Multinational companies",
    "Multinational food companies",
    "Multinational technology companies",
    "Privately held companies based in the United States",
    "Privately held companies based in Germany",
    "Privately held companies based in the United Kingdom",
    "Privately held companies based in Japan",
    "S&P 500 companies",
    "Companies listed on the New York Stock Exchange (A)",
    "Companies listed on the Nasdaq",
    "Companies listed on the London Stock Exchange",
    "Companies listed on the Toronto Stock Exchange",
    "Companies listed on the Tokyo Stock Exchange",
    "Companies listed on the Hong Kong Stock Exchange",
    "Companies listed on the Australian Securities Exchange",
    "Companies listed on Euronext Paris",
    "Companies listed on Euronext Amsterdam",
    "Banks of the United States",
    "Investment banks",
    "Internet companies of the United States",
    "Restaurant chains of the United States",
    "Retail companies of the United States",
    "Automotive companies of Germany",
    "Automotive companies of Japan",
    "Pharmaceutical companies of the United States",
    "Aerospace companies of the United States",
    "Defense companies of the United States",
    "Insurance companies of the United States",
    "Software companies of the United States",
    "Video game companies",
    "Hotel chains",
    "Airlines of the United States",
    "Telecommunications companies of the United States",
    "Mass media companies of the United States",
    "Cosmetics companies",
]


def _fetch_category_members(category: str, max_pages: int = 4) -> list[str]:
    """Fetch up to ~2000 article titles from a Wikipedia category."""
    titles: list[str] = []
    cmcontinue: str | None = None
    pages = 0
    while pages < max_pages:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": "500",
            "cmnamespace": "0",  # main article namespace only
            "format": "json",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
        try:
            with httpx.Client(timeout=20) as client:
                r = client.get(
                    MEDIAWIKI_API, params=params,
                    headers={"User-Agent": USER_AGENT},
                )
            if r.status_code >= 400:
                log.warning("MediaWiki %s -> HTTP %s", category, r.status_code)
                break
            data = r.json()
            members = data.get("query", {}).get("categorymembers", []) or []
            titles.extend(m["title"] for m in members)
            cont = data.get("continue", {})
            cmcontinue = cont.get("cmcontinue")
            pages += 1
            if not cmcontinue:
                break
        except Exception as e:
            log.warning("MediaWiki category fetch failed (%s): %s", category, e)
            break
    return titles


def bulk_import_mediawiki(session: Session, *, max_companies: int | None = None,
                         batch_size: int = 200) -> dict:
    """Acquire companies by enumerating well-curated Wikipedia categories.

    Useful when Wikidata SPARQL is rate-limited or in outage. The MediaWiki
    Action API uses a separate endpoint and is generally available even
    when WDQS is degraded.

    Categories cover global stock exchanges, major privately-held companies
    by country, and topical groupings (banks, automakers, pharma, etc.).
    """
    log.info("Importing companies from Wikipedia category listings")
    all_titles: set[str] = set()
    for cat in MEDIAWIKI_CATEGORIES:
        for title in _fetch_category_members(cat):
            all_titles.add(title)
        if max_companies and len(all_titles) >= max_companies:
            break

    existing_slugs = set(session.exec(select(Company.slug)).all())
    candidate_rows: list[dict] = []
    seen_slugs_this_run: set[str] = set()
    skipped = 0

    for title in all_titles:
        if max_companies is not None and len(candidate_rows) >= max_companies:
            break
        clean = title.strip()
        # Skip disambiguation pages, list pages, and meta-pages
        if not clean or _is_index_or_etf(clean):
            skipped += 1
            continue
        if "(disambiguation)" in clean.lower() or clean.startswith("List of "):
            skipped += 1
            continue
        slug = _slugify(clean)
        if not slug or slug in existing_slugs or slug in seen_slugs_this_run:
            skipped += 1
            continue
        seen_slugs_this_run.add(slug)
        candidate_rows.append({"slug": slug, "name": clean})

    for i in range(0, len(candidate_rows), batch_size):
        chunk = candidate_rows[i:i + batch_size]
        for entry in chunk:
            company = Company(
                slug=entry["slug"],
                name=entry["name"],
                kind=CompanyKind.BOTH,
                domain=None,
                description="Notable company from public Wikipedia.",
            )
            session.add(company)
        session.commit()
        log.info("MediaWiki bulk-import progress: %d added (running total)",
                 i + len(chunk))

    return {
        "added": len(candidate_rows),
        "skipped": skipped,
        "categories_queried": len(MEDIAWIKI_CATEGORIES),
        "raw_titles": len(all_titles),
    }


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
