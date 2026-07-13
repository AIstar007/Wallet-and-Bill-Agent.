# 💳 Wallet & Bill Agent

**A full-stack billing dashboard + AI chat agent that explains charges and finds a better plan — grounded in real DB data and real vector search, not mock responses.**

![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?logo=typescript&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-vector%20search-orange)
![Tests](https://img.shields.io/badge/tests-19%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![CI](https://github.com/AIstar007/wallet-bill-agent/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)

> Built for **The Talent Hack** (Deutsche Telekom Digital Labs) — AI Full Stack Engineer track.
> See [`SUBMISSION.md`](./SUBMISSION.md) for the full hackathon write-up and architecture rationale.

---

## What it does

A customer opens the dashboard and sees their current bill, usage history, and a chat panel. They can ask:
- *"Why is my bill higher this month?"* → answered from the real bill breakdown in the DB
- *"I need a cheaper plan with less data"* → matched against the plan catalog via real FAISS vector search, not a hardcoded lookup table
- *"I need a family plan for 4 lines"* → correctly surfaces the plan that actually matches, ranked by similarity

The agent only **recommends** — it never executes a plan switch or refund itself, same "propose, don't act" pattern as the other two submissions in this hackathon.

## Architecture

```
┌─────────────── Frontend (Next.js 14 + TS + Tailwind) ───────────────┐
│   Dashboard (bill, usage)          │      Chat widget                │
└──────────────────┬──────────────────────────────┬───────────────────┘
                    │ REST                          │ REST
                    ▼                                ▼
┌────────────────────────── Backend (FastAPI) ─────────────────────────┐
│  /bills  /usage  /plans  (SQLAlchemy → SQLite/Postgres)               │
│  /chat → real DB bill lookup + FAISS vector search over plan catalog  │
└────────────────────────────────────────────────────────────────────┘
```

## Quick Start

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Seeds demo data automatically on startup (idempotent — safe to restart)
```

**Frontend** (separate terminal):
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000`.

**Zero setup required to see it work** — `/chat` falls back to stub answer text if no `OPENAI_API_KEY` is set, but the bill lookup, DB queries, and FAISS plan matching are all real regardless. Drop a key into `backend/.env` (copy `.env.example`) for real generated answers.

### Run the tests
```bash
cd backend
pip install -r requirements-dev.txt
cd ..
pytest tests/ --cov=backend --cov-report=term-missing
```
19 tests, 93% coverage — the REST API layer, DB seeding/idempotency, and the FAISS search index directly.

### Docker Compose (full stack, Postgres included)
```bash
docker compose up --build
```

## Design notes

- **`/bills`, `/usage`, `/plans` are real DB-backed endpoints**, not mock dicts — seeded automatically and idempotently on backend startup via a FastAPI `lifespan` handler (not the deprecated `on_event`).
- **Plan matching uses a real FAISS index**, not a static list. It reuses the same dependency-free offline hashing embedder pattern as the AI Engineer submission (`telecom-support-agent`) for consistency across the hackathon — no external model download, works in network-locked environments.
- **The Docker build context matters here**: `backend/Dockerfile` uses package-qualified imports (`backend.main:app`), so it must be built from the repo root with `-f backend/Dockerfile`, not from inside `backend/`. `docker-compose.yml` and CI are both configured for this — worth knowing if you ever restructure the Dockerfile.
- **API base URL is configurable** (`NEXT_PUBLIC_API_URL`), not hardcoded to `localhost:8000` — same for CORS on the backend (`FRONTEND_ORIGIN`) — so this actually works once deployed, not just locally.

## Project structure

```
backend/
├── main.py            # FastAPI app, lifespan DB seeding, configurable CORS
├── db.py               # SQLAlchemy engine/session
├── models.py            # Account, Plan, Bill, UsageRecord
├── seed.py               # idempotent demo data seeding
├── plan_search.py         # offline hashing embedder + FAISS index
├── llm.py                  # real OpenAI client wrapper (used only if API key present)
└── routers/
    ├── bills.py             # /bills /usage /plans — real DB queries, 404 handling
    └── chat.py                # /chat — real DB + real FAISS grounding
frontend/
├── app/page.tsx         # dashboard
└── components/ChatWidget.tsx
tests/                    # 19 tests across API, DB, and FAISS search
```

## What's not built yet

- Auth (would use DTDL's existing SSO)
- Real bill/usage data source integration (currently seeded demo data)
- Token streaming on `/chat`
- pgvector/managed vector DB for production-scale plan catalogs (FAISS-in-process is fine at this size, not at real scale)

## License

MIT
