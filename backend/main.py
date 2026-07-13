import os

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import bills, chat
from backend.db import engine, SessionLocal
from backend.seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed(engine, db)
    finally:
        db.close()
    yield


app = FastAPI(title="Wallet & Bill Agent", version="0.1.0", lifespan=lifespan)

# Comma-separated list of allowed frontend origins. Defaults to local dev;
# set FRONTEND_ORIGIN to your deployed frontend URL (e.g. Vercel) in prod.
allowed_origins = os.environ.get("FRONTEND_ORIGIN", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bills.router, tags=["billing"])
app.include_router(chat.router, tags=["chat"])


@app.get("/health")
def health():
    return {"status": "ok"}
