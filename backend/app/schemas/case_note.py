from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CaseNoteCreate(BaseModel):
    question: str
    answer: str
    legal_references: list[str] = []
    exam_part: str = ""
    core_keyword: str = ""
    importance: str = "Medium"


class CaseNoteOut(BaseModel):
    id: int
    question: str
    answer: str
    legal_references: list[str]
    exam_part: str
    core_keyword: str
    importance: str
    created_at: datetime
