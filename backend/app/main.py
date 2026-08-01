from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.brief import router as brief_router
from app.api.cases import router as cases_router
from app.api.dispatch_workers import router as dispatch_workers_router
from app.api.legal_qa import router as legal_qa_router
from app.api.risk import router as risk_router
from app.api.study import router as study_router
from app.api.tax import router as tax_router
from app.core.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="K-HR Guard", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010", "http://127.0.0.1:3010"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(risk_router)
app.include_router(dispatch_workers_router)
app.include_router(cases_router)
app.include_router(study_router)
app.include_router(brief_router)
app.include_router(tax_router)
app.include_router(legal_qa_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
