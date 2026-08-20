"""오늘 기분 체크인 + 작은 성취 카드.

무거운 상담 업무 사이 잠깐 숨 돌리라고 넣는 기능이라 로직은
일부러 얕게 유지한다 - 복잡한 감정분석이나 추천 없이, 오늘 하루를
가볍게 기록하고 스스로 해낸 걸 눈으로 확인하는 정도.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_USER
from app.models.case_note import CaseNote
from app.models.exam_question_progress import ExamQuestionProgress
from app.models.mood_checkin import MOOD_VALUES, MoodCheckin

HEALING_QUOTES = [
    "오늘도 여러 사람의 질문에 답하느라 애쓰셨어요.",
    "완벽하지 않아도 괜찮아요, 오늘 한 만큼이면 충분해요.",
    "잠깐 어깨를 펴고 크게 숨 한 번 쉬어보세요.",
    "지금 이 순간의 나에게 조금 다정해도 괜찮아요.",
    "바쁜 하루 중에도 이 페이지를 열어준 것만으로 잘하고 있는 거예요.",
    "따뜻한 차 한 잔 마실 여유, 지금 가져보는 건 어때요.",
    "오늘의 어려운 질문 하나, 내일의 나를 더 단단하게 만들어요.",
    "잘 모르겠으면 잠깐 멈춰도 돼요. 서두르지 않아도 괜찮아요.",
    "지금까지 쌓아온 것들이 생각보다 많다는 걸 잊지 마세요.",
    "누군가의 하루를 도왔다는 것, 그 자체로 의미 있는 일이에요.",
    "힘든 상담이 있었다면, 그 감정을 잠시 내려놓고 가도 돼요.",
    "오늘 하루도 나만의 속도로 잘 걸어가고 있어요.",
    "작은 성취도 성취예요. 스스로를 인정해주세요.",
    "가끔은 아무것도 안 하고 그냥 멍 때려도 괜찮아요.",
    "당신의 노력은 화면 너머 누군가에게 분명히 닿고 있어요.",
]

MOOD_RESPONSES: dict[str, str] = {
    "great": "오늘 컨디션 최고네요! 이 기세로 가볍게 이어가봐요.",
    "good": "좋은 하루를 보내고 계시는군요. 잘하고 있어요.",
    "okay": "그냥저냥한 하루도 괜찮아요. 무리하지 마세요.",
    "tired": "많이 피곤하셨겠어요. 잠깐이라도 쉬어가는 시간 가지세요.",
    "stressed": "힘든 하루였군요. 지금 이 순간만큼은 잠시 내려놓아도 괜찮아요.",
}


def _today_quote(today: date) -> str:
    return HEALING_QUOTES[today.timetuple().tm_yday % len(HEALING_QUOTES)]


def record_mood(
    db: Session, mood: str, note: str = "", user: str = DEFAULT_USER
) -> MoodCheckin:
    if mood not in MOOD_VALUES:
        raise ValueError(f"알 수 없는 감정 값: {mood}")

    today = date.today()
    existing = (
        db.query(MoodCheckin)
        .filter(MoodCheckin.created_by == user, MoodCheckin.checkin_date == today)
        .first()
    )
    if existing:
        existing.mood = mood
        existing.note = note
        db.commit()
        db.refresh(existing)
        return existing

    checkin = MoodCheckin(checkin_date=today, mood=mood, note=note, created_by=user)
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


def _streak_days(db: Session, user: str) -> int:
    checkin_dates = {
        row.checkin_date
        for row in db.query(MoodCheckin.checkin_date)
        .filter(MoodCheckin.created_by == user)
        .all()
    }
    if not checkin_dates:
        return 0

    today = date.today()
    cursor = today if today in checkin_dates else today - timedelta(days=1)
    streak = 0
    while cursor in checkin_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def get_today_summary(db: Session, user: str = DEFAULT_USER) -> dict:
    today = date.today()

    checkin = (
        db.query(MoodCheckin)
        .filter(MoodCheckin.created_by == user, MoodCheckin.checkin_date == today)
        .first()
    )

    cases_today = (
        db.query(CaseNote)
        .filter(CaseNote.created_by == user)
        .filter(_same_day(CaseNote.created_at, today))
        .count()
    )
    exam_new_today = (
        db.query(ExamQuestionProgress)
        .filter(ExamQuestionProgress.created_by == user)
        .filter(_same_day(ExamQuestionProgress.created_at, today))
        .count()
    )

    return {
        "mood_today": checkin.mood if checkin else None,
        "mood_note": checkin.note if checkin else "",
        "mood_response": MOOD_RESPONSES.get(checkin.mood) if checkin else None,
        "streak_days": _streak_days(db, user),
        "quote": _today_quote(today),
        "cases_today": cases_today,
        "exam_new_today": exam_new_today,
    }


def _same_day(column, day: date):
    return func.date(column) == day.isoformat()
