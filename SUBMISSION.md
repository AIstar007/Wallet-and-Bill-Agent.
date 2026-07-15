# Wallet & Bill Agent
**Role target: AI Full Stack Engineer (Open Role 3)**

## Problem
The JD calls out managing WiFi/mobile services, paying bills, and digital wallet as core
DTDL product surfaces. Customers currently have to piece together their bill breakdown,
usage, and plan options across separate screens — there's no single place that explains
"here's what you're paying and why, and here's a better plan if one fits."

## What it does
A full-stack web app: users see their bill + usage dashboard, and can chat with an
AI agent that explains charges in plain language, compares their current plan against
alternatives (grounded in the real plan catalog via RAG), and flags savings opportunities —
read-only, no auto-switching, matching the same "AI proposes, human confirms" pattern used
in the other two submissions.

## Architecture
```
┌─────────────── Frontend (Next.js/React) ───────────────┐
│  Dashboard (bill, usage charts)  │  Chat widget          │
└────────────────────┬─────────────────────┬──────────────┘
                      │ REST                │ REST (streaming)
                      ▼                     ▼
┌────────────────────────── Backend (FastAPI) ─────────────────────────┐
│  /bills   /usage   /plans           │  /chat → RAG + LLM             │
│  (Postgres via SQLAlchemy)          │  (plan catalog in vector DB)   │
└────────────────────────────────────────────────────────────────────┘
```

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind. Chat widget does a plain
  request/response call to `/chat` — not token streaming (that's a reasonable next step, not
  implemented in this scaffold; noted below rather than overclaimed).
- **Backend**: FastAPI + SQLAlchemy + SQLite (Postgres-ready via `DATABASE_URL`) for structured
  bill/usage/plan data; a `/chat` endpoint that does real vector search over the plan catalog
  via FAISS (not just a static list filter) so plan comparisons are grounded in a similarity
  match against the user's query, not the model's memory or a hardcoded response.
- **Reusability**: `/bills`, `/usage`, `/plans` are plain REST endpoints, DB-backed, usable by
  any client (the dashboard, the chat agent's tools, or a future mobile app) — not chat-only
  logic baked into the LLM layer.

## Tech stack
Next.js 14 · TypeScript · Tailwind · FastAPI · SQLite/PostgreSQL · SQLAlchemy · Azure OpenAI API ·
FAISS (vector search) · Docker Compose

## What's in this scaffold
- `backend/main.py` — FastAPI app, lifespan-based DB seeding, configurable CORS
- `backend/routers/bills.py` — bill/usage/plans REST endpoints, real DB queries, 404 handling
- `backend/routers/chat.py` — chat endpoint grounded in real DB data + real FAISS plan search
- `backend/plan_search.py` — offline hashing embedder + FAISS index over the plan catalog
- `backend/models.py` / `backend/db.py` / `backend/seed.py` — SQLAlchemy models, session setup, idempotent demo seeding
- `frontend/app/page.tsx` — dashboard shell, configurable API URL via `NEXT_PUBLIC_API_URL`
- `frontend/components/ChatWidget.tsx` — chat UI component
- `docker-compose.yml` — Postgres + backend + frontend, one command to run locally
- `tests/` — 19 tests covering the API layer, DB seeding, and the FAISS search directly

## Not yet built (next steps if advanced to build round)
- Auth (would use DTDL's existing SSO)
- Real bill/usage data source integration (currently seeded demo data, not a live billing system)
- Token streaming on `/chat` for a more responsive chat UI
- pgvector or a managed vector DB for production-scale plan catalogs (FAISS-in-process is fine at this catalog size, not at real scale)
