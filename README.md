# True Review

The most trusted source for real company culture intelligence. AI-native company review platform that solves the trust, verification, and signal problems of Glassdoor, Blind, Indeed Reviews, Comparably, Fishbowl, and Fairygodboss.

> Free for users. Revenue model: Google AdSense + future premium employer analytics.

## Mission

Verified truth. Real employee sentiment. Transparent moderation. Trustworthy insights. Predictive workplace intelligence.

## Monorepo Layout

```
true-review/
├── web/        → Next.js 16 App Router (deployed to Vercel)
├── api/        → FastAPI + SQLModel + Postgres (deployed to Railway)
├── ios/        → SwiftUI iOS app (Xcode)
├── packages/
│   └── shared/ → Shared schemas (Pydantic ↔ TypeScript via JSON Schema)
└── .github/    → CI/CD workflows
```

## Synced Platforms

| Surface | Where | Trigger |
| --- | --- | --- |
| `web/` | Vercel | Push to `main` → production; PRs → preview URLs |
| `api/` | Railway | Push to `main` → auto-deploy |
| `ios/` | TestFlight (manual) | Xcode Cloud or local archive |
| Source of truth | GitHub | `gh repo view damienmcdade/true-review` |

## Local Dev

```bash
# Web
cd web && npm install && npm run dev      # http://localhost:3000

# API
cd api && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000  # http://localhost:8000

# iOS
cd ios && xcodegen generate && open TrueReview.xcodeproj
```

## Environment Variables

See `.env.example`. After cloning:
- `cd web && vercel env pull .env.local`
- `cd api && railway variables` to inspect

## Monetization

- **Free tier**: All users. Reviews, search, AI copilot, dashboards. Ad-supported via Google AdSense.
- **Premium employers** (Phase 2): Verified company pages, response analytics, sentiment alerts.

## Status

Early scaffold. See [PRD.md](./PRD.md) for the full product vision.
