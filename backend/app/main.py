from __future__ import annotations

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.brief import router as brief_router
from app.api.calculators import router as calculators_router
from app.api.cases import router as cases_router
from app.api.exam import router as exam_router
from app.api.legal_qa import router as legal_qa_router
from app.api.resume import router as resume_router
from app.api.risk import router as risk_router
from app.api.study import router as study_router
from app.api.tax import router as tax_router
from app.api.wellbeing import router as wellbeing_router
from app.core.auth import SharedPasswordAuthMiddleware, warn_if_auth_disabled
from app.core.db import init_db
from app.engines.rag import corpus
from app.engines.rag.vector_store import get_default_store

DEFAULT_DEV_ORIGINS = "http://localhost:3010,http://127.0.0.1:3010"
# 배포 도메인(예: https://k-hr-guard.pages.dev)을 추가하려면 ALLOWED_ORIGINS
# 환경변수에 콤마로 구분해서 넣는다. 미설정 시 로컬 개발 기본값만 허용.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", DEFAULT_DEV_ORIGINS).split(",")
    if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    warn_if_auth_disabled()
    init_db()
    # Render 무료플랜은 재배포/재시작마다 디스크가 초기화돼서 ChromaDB가
    # 비어있는 채로 뜬다 - 비어있으면 매 기동 시 자동으로 다시 채운다
    # (upsert라 중복 걱정 없음). GEMINI_API_KEY 미설정(로컬 테스트 등)이거나
    # API 호출이 실패해도 앱 부팅 자체는 막지 않는다.
    try:
        store = get_default_store()
        if store.count() == 0:
            corpus.ingest_sample_corpus(store)
    except Exception:
        logging.getLogger(__name__).warning(
            "샘플 코퍼스 자동 적재 실패 - /legal-qa/ingest-sample-corpus로 수동 적재 필요",
            exc_info=True,
        )
    yield


app = FastAPI(title="K-HR Guard", lifespan=lifespan)
# 미들웨어는 마지막에 추가한 것이 가장 바깥쪽(요청을 먼저 받음)이 된다.
# CORS가 Auth보다 바깥에 있어야 401 응답에도 CORS 헤더가 붙는다 -
# 순서가 반대면 브라우저가 401을 CORS 에러(net::ERR_FAILED)로 오인해서
# 실제 에러 메시지 대신 통째로 요청이 실패한 것처럼 보인다.
app.add_middleware(SharedPasswordAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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
app.include_router(exam_router)
app.include_router(wellbeing_router)
app.include_router(resume_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
