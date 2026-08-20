from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engines import compliance_check
from app.engines.gemini_client import GeminiNotConfiguredError, GeminiQuotaExceededError
from app.schemas.compliance_check import ComplianceCheckRequest, ComplianceCheckResult

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post("/check", response_model=ComplianceCheckResult)
def check(payload: ComplianceCheckRequest) -> dict:
    try:
        return compliance_check.check_compliance(payload.situation)
    except GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
