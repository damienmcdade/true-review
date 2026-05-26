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

## Live URLs

| Surface | URL |
| --- | --- |
| Web (production) | https://true-review-kappa.vercel.app |
| API | https://truereview-api-production.up.railway.app |
| API docs | https://truereview-api-production.up.railway.app/docs |
| GitHub | https://github.com/damienmcdade/true-review |
| Vercel project | https://vercel.com/damienmcdade17-2595s-projects/true-review |
| Railway project | https://railway.com/project/cd42df3c-1ae1-453a-8302-30838cd63593 |

## Railway state notes

The keeper database is `Postgres-O9KV`, wired into the API via `${{Postgres-O9KV.DATABASE_URL}}`.

Three orphan volumes (`postgres-volume`, `postgres-volume-YjHK`, `postgres-volume-kWLs`) appear in `railway volume list` and the dashboard. Their `VolumeInstance` records are in `state: DELETED` (no storage provisioned, not billable). Railway's `volumeDelete` mutation returns success but doesn't remove the parent `Volume` metadata — that's a server-side quirk. If you want them gone from the UI, open a Railway support ticket.

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
