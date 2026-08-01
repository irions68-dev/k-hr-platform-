from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.brief import router as brief_router
from app.api.calculators import router as calculators_router
from app.api.cases import router as cases_router
from app.api.legal_qa import router as legal_qa_router
from app.api.risk import router as risk_router
from app.api.study import router as study_router
from app.api.tax import router as tax_router
from app.core.auth import SharedPasswordAuthMiddleware, warn_if_auth_disabled
from app.core.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    warn_if_auth_disabled()
    init_db()
    yield


app = FastAPI(title="K-HR Guard", lifespan=lifespan)
# 미들웨어는 마지막에 추가한 것이 가장 바깥쪽(요청을 먼저 받음)이 된다.
# CORS가 Auth보다 바깥에 있어야 401 응답에도 CORS 헤더가 붙는다 -
# 순서가 반대면 브라우저가 401을 CORS 에러(net::ERR_FAILED)로 오인해서
# 실제 에러 메시지 대신 통째로 요청이 실패한 것처럼 보인다.
app.add_middleware(SharedPasswordAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3010", "http://127.0.0.1:3010"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(risk_router)
app.include_router(calculators_router)
app.include_router(cases_router)
app.include_router(study_router)
app.include_router(brief_router)
app.include_router(tax_router)
app.include_router(legal_qa_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
