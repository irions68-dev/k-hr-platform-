from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engines import client_negotiation
from app.schemas.client_negotiation import ClientNegotiationRequest, ClientNegotiationResult

router = APIRouter(prefix="/client-negotiation", tags=["client-negotiation"])


@router.post("/draft", response_model=ClientNegotiationResult)
def draft(payload: ClientNegotiationRequest) -> dict:
    try:
        return client_negotiation.generate_negotiation_draft(
            payload.context_notes, payload.purpose
        )
    except client_negotiation.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except client_negotiation.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
