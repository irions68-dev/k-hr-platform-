from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.engines import message_draft
from app.schemas.message_draft import MessageDraftRequest, MessageDraftResult

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/draft", response_model=MessageDraftResult)
def draft(payload: MessageDraftRequest) -> dict:
    try:
        return message_draft.generate_drafts(payload.situation, payload.situation_type)
    except message_draft.GeminiNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except message_draft.GeminiQuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
