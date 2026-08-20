from __future__ import annotations

from pydantic import BaseModel, Field


class MessageDraftRequest(BaseModel):
    situation: str = Field(min_length=1)
    situation_type: str = ""


class MessageDraftResult(BaseModel):
    client_email: str
    worker_message: str
    interviewer_memo: str
