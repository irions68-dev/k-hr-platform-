from __future__ import annotations

from pydantic import BaseModel, Field


class ComplianceCheckRequest(BaseModel):
    situation: str = Field(min_length=1)


class ComplianceCheckResult(BaseModel):
    risk_level: str
    risk_summary: str
    legal_references: list[str]
    pitch: str
