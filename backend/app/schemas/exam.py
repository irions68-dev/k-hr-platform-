from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class DailyQuestion(BaseModel):
    id: str
    subject: str
    number: int
    question: str
    choices: list[str]


class ExamAttemptSubmit(BaseModel):
    question_id: str
    selected_index: int = Field(ge=1, le=5)


class ExamAttemptResult(BaseModel):
    correct: bool
    answer_index: int
    explanation: str | None
    keywords: list[str]
    next_review_date: date


class ExamStats(BaseModel):
    total_questions: int
    attempted_questions: int
    total_attempts: int
    total_correct: int
    accuracy: float | None
