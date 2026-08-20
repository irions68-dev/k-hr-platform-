from __future__ import annotations

from pydantic import BaseModel, Field


class ClientNegotiationRequest(BaseModel):
    context_notes: str = Field(min_length=1)
    purpose: str = Field(min_length=1)


class ClientNegotiationResult(BaseModel):
    approach_notes: str
    email_draft: str
    key_points: list[str]
