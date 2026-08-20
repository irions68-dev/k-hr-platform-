from __future__ import annotations

from pydantic import BaseModel, Field


class ComplaintDefenseRequest(BaseModel):
    complaint_text: str = Field(min_length=1)


class ComplaintDefenseResult(BaseModel):
    defense_response: str
    legal_basis: list[str]
    legal_basis_explanation: str
    caution_note: str
