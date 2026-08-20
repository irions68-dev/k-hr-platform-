from __future__ import annotations

from pydantic import BaseModel, Field


class AttritionSignalRequest(BaseModel):
    conversation_notes: str = Field(min_length=1)


class AttritionSignalResult(BaseModel):
    observed_signals: list[str]
    suggested_approach: str
    talking_points: list[str]
    caution_note: str
