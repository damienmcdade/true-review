# True Review — Product Requirements Document

## 1. Product Vision

The most trusted source for real company culture intelligence. A privacy-first, AI-native platform where verified current and former employees share workplace truth — with cryptographic proof-of-employment, transparent moderation, and AI-powered pattern recognition that makes raw reviews actionable.

## 2. Core Differentiators

1. **Zero-knowledge employment verification** — prove you worked somewhere without exposing identity.
2. **Public moderation logs** — every removal/edit is logged with reason.
3. **Trust score per reviewer** — credibility transparent, not popularity.
4. **AI copilot** — "what's it really like here?" answered with citations to underlying reviews.
5. **Real-time company health** — sentiment, layoff probability, leadership confidence, burnout indicators.
6. **Privacy-first architecture** — metadata minimization, anti-doxxing systems.
7. **No paid suppression** — companies cannot remove negative reviews; only flag factual errors.

## 3. Target Users

- **Job seekers** — researching companies before applying/accepting.
- **Current employees** — comparing their experience, salary, mobility.
- **Recently departed employees** — sharing experiences without retaliation risk.
- **Journalists/researchers** — aggregate workplace data.
- **Employers (Phase 2)** — verified company responses, sentiment analytics.

## 4. Information Architecture

```
/                          → Homepage (trending companies, AI insights)
/c/[company]               → Company page (overview, trust score, ratings)
/c/[company]/reviews       → All reviews, filterable
/c/[company]/health        → Real-time health dashboard
/c/[company]/ask           → AI copilot for this company
/c/[company]/compare       → Compare vs. competitors
/search                    → Advanced search
/review/new                → Submit a review (verification gated)
/me                        → Reviewer dashboard (trust score, history)
/transparency              → Moderation logs, removed content explanations
/verify                    → Employment verification flow
```

## 5. Database Schema (initial)

See `api/app/models.py`. Core entities:
- `users` (anonymous, trust-scored)
- `companies` (canonical, dedup'd)
- `employment_proofs` (verified, encrypted)
- `reviews` (long-form, multi-dimensional ratings)
- `review_signals` (AI-detected patterns)
- `moderation_log` (public, immutable)
- `trust_events` (reputation deltas)

## 6. Trust & Verification Engine

- **Employment proof tiers**:
  - T1: Work email OTP (highest trust)
  - T2: LinkedIn OAuth + employment match
  - T3: Document upload (W-2 redacted, offer letter) — manual review
  - T4: Payroll API (Argyle, Pinwheel) — gold standard
- **Reviewer trust score**: function of verification tier, review consistency, community validation, time on platform, evidence quality.

## 7. AI System Design

- **Provider**: Vercel AI Gateway with Anthropic Claude (primary), fallback to OpenAI/Gemini.
- **Use cases**:
  - Summarize company sentiment (RAG over reviews)
  - Detect fake review patterns (classifier + embedding outlier detection)
  - Extract themes (clustering on embeddings)
  - Answer "is this company stable?" (RAG + financial signals)
  - Predict burnout risk (review sentiment trends + churn signals)
- **Vector store**: Postgres + pgvector.
- **Embedding model**: `text-embedding-3-small` via AI Gateway.

## 8. Moderation Architecture

- **Layer 1**: AI pre-check (toxicity, PII, named individuals).
- **Layer 2**: Community flagging.
- **Layer 3**: Human review team (no employer ties).
- **Public log**: Every action timestamped, reasoned, appealable.

## 9. Tech Stack

- **Web**: Next.js 16 App Router, React Server Components, Tailwind, shadcn/ui.
- **API**: FastAPI, SQLModel, Postgres + pgvector, Redis (Upstash).
- **AI**: Vercel AI Gateway → Claude Opus 4.7.
- **iOS**: SwiftUI, Combine, native auth via Sign in with Apple.
- **Auth**: Clerk (web) → JWT mirrored to API. Anonymous-by-default sessions.
- **Hosting**: Vercel (web) + Railway (api+db).

## 10. Monetization

- **Phase 1 (now)**: Google AdSense on free public pages. Privacy-respecting placements only; no ads on review-write flow or verification pages.
- **Phase 2**: Premium employer subscriptions (verified responses, sentiment alerts, hiring insights).
- **Phase 3**: Anonymous aggregated workplace data licensing (consent-gated).

## 11. MVP Roadmap

**M1 (this scaffold)**: Repo, deployments, basic web shell.
**M2**: Auth + verification (T1 work email).
**M3**: Submit + browse reviews. Company pages.
**M4**: AI summary + copilot.
**M5**: Trust score v1. Moderation log.
**M6**: iOS read-only app.
**M7**: Public beta.

## 12. Risks

- Legal: defamation exposure. Mitigated by verification + factual-claim moderation + Section 230 posture.
- Manipulation: bot/coordinated attacks. Mitigated by verification tiers + AI anomaly detection.
- Trust loss if perceived as biased. Mitigated by public moderation logs + open algorithms.
