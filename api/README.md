# True Review API

FastAPI + SQLModel + Postgres backend deployed to Railway.

## Local dev

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for OpenAPI.

## Environment

| Var | Purpose |
| --- | --- |
| `DATABASE_URL` | Postgres connection string. Railway injects this. |
| `JWT_SECRET` | HMAC secret for tokens. |
| `CORS_ORIGINS` | Comma-separated allowed origins. |
| `ANTHROPIC_API_KEY` | Claude key for AI summaries. |

## Endpoints (initial)

- `GET /health` — liveness probe
- `GET /companies?q=...` — search
- `GET /companies/{slug}` — page + health
- `GET /moderation/log` — public transparency log
