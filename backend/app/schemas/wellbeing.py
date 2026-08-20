from __future__ import annotations

from pydantic import BaseModel


class MoodCheckinCreate(BaseModel):
    mood: str
    note: str = ""


class TodayWellbeing(BaseModel):
    mood_today: str | None
    mood_note: str
    mood_response: str | None
    streak_days: int
    quote: str
    cases_today: int
    exam_new_today: int
