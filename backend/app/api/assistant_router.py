from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engines import assistant_router
from app.schemas.assistant_router import AssistantRouteRequest, AssistantRouteResult

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/route", response_model=AssistantRouteResult)
def route(payload: AssistantRouteRequest) -> dict:
    try:
        return assistant_router.route(payload.text)
    except assistant_router.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except assistant_router.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
