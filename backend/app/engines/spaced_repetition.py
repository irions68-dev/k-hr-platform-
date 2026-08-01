"""SM-2 기반 간격반복(Spaced Repetition) 스케줄링 로직.

오답노트/키워드를 쌓아두기만 하면 결국 다시 보지 않게 되므로,
복습 시점을 자동으로 계산해 실제로 복습하게 만드는 것이 목적이다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

MIN_EASE_FACTOR = 1.3
DEFAULT_EASE_FACTOR = 2.5
PASSING_QUALITY = 3  # 0~5 중 3 미만이면 회상 실패로 간주하고 처음부터 다시


@dataclass
class ReviewState:
    interval_days: int
    ease_factor: float
    repetitions: int


def schedule_next_review(
    quality: int,
    state: ReviewState,
    reference_date: date | None = None,
) -> dict:
    """SM-2 알고리즘으로 다음 복습일과 상태를 계산한다.

    Args:
        quality: 이번 복습에서의 회상 품질(0~5, 5가 완벽하게 기억).
        state: 직전까지의 반복 상태.
        reference_date: 복습을 수행한 날짜(생략 시 오늘).
    """
    if not 0 <= quality <= 5:
        raise ValueError("quality must be between 0 and 5")

    today = reference_date or date.today()

    if quality < PASSING_QUALITY:
        repetitions = 0
        interval_days = 1
    else:
        repetitions = state.repetitions + 1
        if repetitions == 1:
            interval_days = 1
        elif repetitions == 2:
            interval_days = 6
        else:
            interval_days = round(state.interval_days * state.ease_factor)

    ease_factor = state.ease_factor + (
        0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
    )
    ease_factor = max(MIN_EASE_FACTOR, round(ease_factor, 2))

    return {
        "interval_days": interval_days,
        "ease_factor": ease_factor,
        "repetitions": repetitions,
        "next_review_date": today + timedelta(days=interval_days),
    }
