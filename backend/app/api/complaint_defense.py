from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engines import complaint_defense
from app.engines.gemini_client import GeminiNotConfiguredError, GeminiQuotaExceededError
from app.schemas.complaint_defense import ComplaintDefenseRequest, ComplaintDefenseResult

router = APIRouter(prefix="/complaint-defense", tags=["complaint-defense"])


@router.post("/generate", response_model=ComplaintDefenseResult)
def generate(payload: ComplaintDefenseRequest) -> dict:
    try:
        return complaint_defense.generate_defense(payload.complaint_text)
    except GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
