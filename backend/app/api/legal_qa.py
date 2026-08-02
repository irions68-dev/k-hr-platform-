from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engines.rag import corpus, generation, pipeline
from app.engines.rag.vector_store import get_default_store
from app.schemas.legal_qa import AskRequest

router = APIRouter(prefix="/legal-qa", tags=["legal-qa"])


@router.post("/ingest-sample-corpus")
def ingest_sample_corpus() -> dict:
    count = corpus.ingest_sample_corpus()
    return {"ingested_count": count, "total_documents": get_default_store().count()}


@router.post("/ask")
def ask(payload: AskRequest) -> dict:
    try:
        return pipeline.ask(payload.question, top_k=payload.top_k)
    except generation.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except generation.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
