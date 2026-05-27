"""Seed the database with **clearly demonstrative** companies + reviews.

LEGAL NOTE:
- All seed reviews are marked `is_demo=True`. Frontend shows a "DEMO" badge.
- We avoid attributing strong negative opinions to real, named companies.
- Scam-flagged seed entries use unmistakably fictional names with `-demo`
  suffix so they can never be mistaken for real businesses.

This file is idempotent — safe to re-run on every boot. New companies
get added; existing companies' demo content gets topped up but never
replaced.
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Session, select

from .models import Company, CompanyKind, Review, ReviewType, User, VerificationTier


# 20+ companies so search lands on something useful for most queries.
SAMPLE_COMPANIES = [
    {"name": "Stripe", "slug": "stripe", "kind": "employer", "domain": "stripe.com",
     "description": "Payments infrastructure for the internet."},
    {"name": "Anthropic", "slug": "anthropic", "kind": "employer", "domain": "anthropic.com",
     "description": "AI safety company that builds Claude."},
    {"name": "Shopify", "slug": "shopify", "kind": "both", "domain": "shopify.com",
     "description": "Commerce platform powering millions of merchants."},
    {"name": "Patagonia", "slug": "patagonia", "kind": "both", "domain": "patagonia.com",
     "description": "Outdoor apparel; mission-driven sustainability brand."},
    {"name": "Costco", "slug": "costco", "kind": "merchant", "domain": "costco.com",
     "description": "Membership warehouse retailer."},
    {"name": "Apple", "slug": "apple", "kind": "both", "domain": "apple.com",
     "description": "Consumer electronics and services."},
    {"name": "Microsoft", "slug": "microsoft", "kind": "employer", "domain": "microsoft.com",
     "description": "Software, cloud, devices."},
    {"name": "Netflix", "slug": "netflix", "kind": "employer", "domain": "netflix.com",
     "description": "Streaming entertainment service."},
    {"name": "Amazon", "slug": "amazon", "kind": "both", "domain": "amazon.com",
     "description": "Online retail and cloud services."},
    {"name": "Google", "slug": "google", "kind": "employer", "domain": "google.com",
     "description": "Search, ads, cloud, devices."},
    {"name": "Tesla", "slug": "tesla", "kind": "both", "domain": "tesla.com",
     "description": "Electric vehicles and energy."},
    {"name": "Spotify", "slug": "spotify", "kind": "both", "domain": "spotify.com",
     "description": "Audio streaming and podcast platform."},
    {"name": "Airbnb", "slug": "airbnb", "kind": "both", "domain": "airbnb.com",
     "description": "Marketplace for short-term lodging."},
    {"name": "GitHub", "slug": "github", "kind": "employer", "domain": "github.com",
     "description": "Software collaboration platform owned by Microsoft."},
    {"name": "Figma", "slug": "figma", "kind": "employer", "domain": "figma.com",
     "description": "Collaborative interface design tool."},
    {"name": "Notion", "slug": "notion", "kind": "employer", "domain": "notion.so",
     "description": "All-in-one workspace for notes, docs, and projects."},
    {"name": "Vercel", "slug": "vercel", "kind": "both", "domain": "vercel.com",
     "description": "Frontend cloud platform behind Next.js."},
    {"name": "Cloudflare", "slug": "cloudflare", "kind": "both", "domain": "cloudflare.com",
     "description": "Edge network, DDoS protection, developer platform."},
    {"name": "REI", "slug": "rei", "kind": "merchant", "domain": "rei.com",
     "description": "Outdoor co-op retailer."},
    {"name": "Trader Joe's", "slug": "trader-joes", "kind": "both", "domain": "traderjoes.com",
     "description": "Privately held grocery chain."},
    # Fictional scam-flagged demos (clearly marked)
    {"name": "Acme Phishing Demo Co", "slug": "acme-phishing-demo",
     "kind": "merchant", "domain": "acme-phishing-demo.example",
     "description": "FICTIONAL demonstration entity used to showcase the scam-report flow.",
     "is_scam_flagged": True, "scam_severity": 0.88},
    {"name": "ExampleScam Industries Demo", "slug": "examplescam-industries-demo",
     "kind": "merchant", "domain": "examplescam-industries-demo.example",
     "description": "FICTIONAL demonstration entity used to showcase the scam-report flow.",
     "is_scam_flagged": True, "scam_severity": 0.92},
]


# Multiple demo reviews per company so search results lead to populated pages.
# Reviews stay deliberately neutral / lightly opinionated and are tagged `is_demo`.
EMPLOYMENT_REVIEWS = [
    # (slug, rating, title, body, department, status)
    ("stripe", 4.4, "Demo — strong engineering culture",
     "Demo content. Reviewers commonly note a high technical bar and well-documented internal tools.", "Engineering", "current"),
    ("stripe", 3.8, "Demo — fast pace, watch for burnout",
     "Demo content. Pace can be intense in customer-facing teams; managers vary on protecting focus time.", "Operations", "former"),
    ("anthropic", 4.7, "Demo — research-aligned",
     "Demo content. Common feedback highlights psychological safety and a calm decision-making cadence.", "Research", "current"),
    ("anthropic", 4.3, "Demo — collaborative onboarding",
     "Demo content. New hires often mention generous context-sharing and pairing.", "Engineering", "current"),
    ("shopify", 4.1, "Demo — autonomy at the IC level",
     "Demo content. Individual contributors report a lot of trust and ownership of outcomes.", "Engineering", "current"),
    ("shopify", 3.6, "Demo — reorgs slow decisions",
     "Demo content. Recent organizational changes are frequently cited as a source of friction.", "Product", "former"),
    ("microsoft", 4.2, "Demo — steady environment",
     "Demo content. Reviewers cite improved leadership and stable benefits.", "Engineering", "current"),
    ("microsoft", 4.0, "Demo — strong work-life balance on many teams",
     "Demo content. Balance varies by org, but most reviewers report manageable hours.", "Sales", "current"),
    ("netflix", 3.7, "Demo — high autonomy, high stakes",
     "Demo content. Reviewers cite generous pay and the well-known performance culture.", "Engineering", "current"),
    ("netflix", 3.3, "Demo — performance-review pressure",
     "Demo content. Keeper test and feedback cycles are recurring themes.", "Content", "former"),
    ("patagonia", 4.6, "Demo — mission alignment",
     "Demo content. Sustainability values are consistently described as genuine.", "Retail", "current"),
    ("patagonia", 4.2, "Demo — pay below tech, balance above",
     "Demo content. Compensation is below tech-industry, but workplace flexibility is consistently praised.", "HQ", "current"),
    ("google", 3.9, "Demo — perks remain strong",
     "Demo content. Compensation and benefits stay top-tier; reviewers note slower project velocity than before.", "Engineering", "current"),
    ("amazon", 3.0, "Demo — varies sharply by team",
     "Demo content. Reviewers describe both excellent and grueling teams within the same org.", "Operations", "former"),
    ("tesla", 2.9, "Demo — fast change, intense pace",
     "Demo content. Reviewers note inspiring mission but unsustainable hours on some teams.", "Engineering", "former"),
    ("spotify", 4.0, "Demo — squad model still appreciated",
     "Demo content. Reviewers cite autonomy and clear team missions.", "Engineering", "current"),
    ("airbnb", 3.8, "Demo — remote-friendly",
     "Demo content. Live-and-work-anywhere policy is consistently called out as a positive.", "Engineering", "current"),
    ("github", 4.1, "Demo — remote-first norms",
     "Demo content. Async-first culture is appreciated by ICs.", "Engineering", "current"),
    ("figma", 4.4, "Demo — design-centric across functions",
     "Demo content. Reviewers note strong product sensibility across PM, engineering, and design.", "Design", "current"),
    ("notion", 4.0, "Demo — small-team feel scaling",
     "Demo content. Reviewers describe culture as still feeling small as the company has grown.", "Product", "current"),
    ("vercel", 4.3, "Demo — strong DX focus",
     "Demo content. Reviewers note product velocity and a healthy engineering culture.", "Engineering", "current"),
    ("cloudflare", 4.0, "Demo — mission-driven engineering",
     "Demo content. Reviewers cite interesting technical problems and a clear company narrative.", "Engineering", "current"),
]

SHOPPING_REVIEWS = [
    ("patagonia", 4.8, "Demo — durable goods, real warranty",
     "Demo content. Reviewers consistently mention long product life and responsive warranty service.", "Down jacket", 280.0),
    ("patagonia", 4.5, "Demo — gear holds up over years",
     "Demo content. Long-term durability is a recurring theme.", "Backpack", 130.0),
    ("costco", 4.5, "Demo — membership pays off",
     "Demo content. Reviewers cite bulk staples and generous return policy.", "Executive membership", 130.0),
    ("costco", 4.3, "Demo — Kirkland brand consistently good",
     "Demo content. House-brand value comes up a lot.", "Kirkland goods (basket)", 50.0),
    ("apple", 4.3, "Demo — in-store service strong",
     "Demo content. Genius Bar walk-in support gets repeat praise.", "Laptop service", 0.0),
    ("apple", 4.1, "Demo — premium pricing, premium build",
     "Demo content. Mixed value sentiment depending on the product line.", "iPhone", 999.0),
    ("amazon", 3.8, "Demo — Prime delivery reliable for first-party",
     "Demo content. Third-party seller variance is the most frequent caveat.", "Prime", 139.0),
    ("amazon", 3.4, "Demo — third-party seller quality varies",
     "Demo content. Reviewers recommend reading seller reviews carefully.", "General order", 45.0),
    ("shopify", 4.2, "Demo — solid commerce platform",
     "Demo content. Reviewers describe reliable storefronts; transaction-fee structure gets discussed.", "Shopify Basic plan", 39.0),
    ("apple", 4.0, "Demo — accessory pricing is high",
     "Demo content. Cables and adapters draw the most complaints.", "Accessory pack", 80.0),
    ("rei", 4.4, "Demo — knowledgeable staff",
     "Demo content. In-store expertise and member dividend get repeat callouts.", "Tent", 350.0),
    ("rei", 4.5, "Demo — generous return policy",
     "Demo content. One-year return window is frequently cited.", "Hiking shoes", 160.0),
    ("trader-joes", 4.4, "Demo — house brands consistently good",
     "Demo content. Private-label items are the recurring positive.", "Frozen meals", 30.0),
    ("trader-joes", 4.2, "Demo — checkout staff friendly",
     "Demo content. Customer service is a consistent positive.", "Weekly groceries", 90.0),
    ("spotify", 3.9, "Demo — solid catalog, mixed UI changes",
     "Demo content. Catalog breadth gets praise; UI redesigns get mixed reactions.", "Premium subscription", 11.99),
    ("airbnb", 3.6, "Demo — quality varies by host",
     "Demo content. Listing accuracy and cleaning fees are common gripes.", "Stay (3 nights)", 420.0),
    ("vercel", 4.4, "Demo — fastest deploys we tried",
     "Demo content. Speed and DX are the recurring positives.", "Pro plan", 20.0),
    ("cloudflare", 4.5, "Demo — strong free tier",
     "Demo content. Reviewers note generous free-tier feature set.", "Free plan", 0.0),
    ("tesla", 3.1, "Demo — car experience strong, service mixed",
     "Demo content. Driving experience consistently praised; service wait times vary.", "Model Y", 49990.0),
    ("github", 4.5, "Demo — copilot productivity",
     "Demo content. Reviewers cite measurable productivity gains.", "Copilot subscription", 10.0),
]

SCAM_REPORTS = [
    ("acme-phishing-demo", 1.0, "Demo — non-delivery scenario",
     "FICTIONAL demo content. Illustrates a non-delivery scam report flow.", "non_delivery", 89.0),
    ("acme-phishing-demo", 1.0, "Demo — phishing follow-up scenario",
     "FICTIONAL demo content. Illustrates a phishing followup report.", "phishing", 0.0),
    ("acme-phishing-demo", 1.0, "Demo — counterfeit scenario",
     "FICTIONAL demo content. Illustrates a counterfeit-product report.", "counterfeit", 145.0),
    ("examplescam-industries-demo", 1.0, "Demo — fund-withdrawal scenario",
     "FICTIONAL demo content. Illustrates a fake-investment platform report.", "fake_invoice", 2000.0),
    ("examplescam-industries-demo", 1.0, "Demo — deepfake-endorsement scenario",
     "FICTIONAL demo content. Illustrates a fake-celebrity-endorsement report.", "phishing", 0.0),
    ("examplescam-industries-demo", 1.0, "Demo — third report demonstrating threshold",
     "FICTIONAL demo content. Demonstrates auto-flag threshold of 3.", "fake_invoice", 1500.0),
]


def ensure_user(session: Session, handle: str, tier: VerificationTier) -> User:
    existing = session.exec(select(User).where(User.handle == handle)).first()
    if existing:
        return existing
    user = User(handle=handle, trust_score=0.7, verification_tier=tier)
    session.add(user)
    session.flush()
    return user


def run_seed(session: Session) -> dict:
    added_companies = 0
    added_reviews = 0

    for c in SAMPLE_COMPANIES:
        existing = session.exec(select(Company).where(Company.slug == c["slug"])).first()
        if existing:
            continue
        company = Company(
            slug=c["slug"],
            name=c["name"],
            kind=CompanyKind(c["kind"]),
            domain=c.get("domain"),
            description=c.get("description"),
            is_scam_flagged=c.get("is_scam_flagged", False),
            scam_severity=c.get("scam_severity", 0.0),
        )
        session.add(company)
        added_companies += 1

    session.commit()

    # Each review category seeds with its own demo author so the verifier-tier
    # badges display realistically: employment authors are T1 work-email-verified,
    # shopping authors carry the per-purchase receipt tier, scam reporters carry
    # the fraud-evidence tier.
    emp_author = ensure_user(session, "demo_employee", VerificationTier.T1_EMAIL)
    shop_author = ensure_user(session, "demo_shopper", VerificationTier.T_RECEIPT)
    scam_author = ensure_user(session, "demo_scam_reporter", VerificationTier.T_FRAUD_EVIDENCE)

    def add_review(slug: str, kind: ReviewType, rating: float, title: str, body: str,
                   author: User, **kw) -> None:
        nonlocal added_reviews
        company = session.exec(select(Company).where(Company.slug == slug)).first()
        if not company:
            return
        existing = session.exec(
            select(Review).where(Review.company_id == company.id, Review.title == title)
        ).first()
        if existing:
            return
        review = Review(
            company_id=company.id,
            author_id=author.id,
            review_type=kind,
            title=title,
            body=body,
            rating_overall=rating,
            is_demo=True,
            **kw,
        )
        session.add(review)
        if kind == ReviewType.SCAM_REPORT:
            company.scam_reports_count = (company.scam_reports_count or 0) + 1
            company.last_scam_report_at = datetime.utcnow()
            session.add(company)
        added_reviews += 1

    for slug, rating, title, body, dept, status in EMPLOYMENT_REVIEWS:
        add_review(slug, ReviewType.EMPLOYMENT, rating, title, body, emp_author,
                   department=dept, employment_status=status)
    for slug, rating, title, body, product, amount in SHOPPING_REVIEWS:
        add_review(slug, ReviewType.SHOPPING, rating, title, body, shop_author,
                   product_or_service=product, purchase_amount=amount)
    for slug, rating, title, body, category, amount in SCAM_REPORTS:
        add_review(slug, ReviewType.SCAM_REPORT, rating, title, body, scam_author,
                   scam_category=category, money_lost=amount)

    session.commit()
    return {"added_companies": added_companies, "added_reviews": added_reviews}
