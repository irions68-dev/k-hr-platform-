from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engines import attrition_signal
from app.schemas.attrition_signal import AttritionSignalRequest, AttritionSignalResult

router = APIRouter(prefix="/attrition-signal", tags=["attrition-signal"])


@router.post("/analyze", response_model=AttritionSignalResult)
def analyze(payload: AttritionSignalRequest) -> dict:
    try:
        return attrition_signal.analyze_signals(payload.conversation_notes)
    except attrition_signal.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except attrition_signal.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
