from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str
    top_k: int = Field(default=3, ge=1, le=10)
