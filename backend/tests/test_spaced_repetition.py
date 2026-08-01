from datetime import date

import pytest

from app.engines.spaced_repetition import ReviewState, schedule_next_review


def test_first_successful_review_sets_interval_to_1_day():
    state = ReviewState(interval_days=0, ease_factor=2.5, repetitions=0)
    result = schedule_next_review(quality=4, state=state, reference_date=date(2026, 1, 1))
    assert result["repetitions"] == 1
    assert result["interval_days"] == 1
    assert result["next_review_date"] == date(2026, 1, 2)


def test_second_successful_review_sets_interval_to_6_days():
    state = ReviewState(interval_days=1, ease_factor=2.5, repetitions=1)
    result = schedule_next_review(quality=4, state=state, reference_date=date(2026, 1, 1))
    assert result["repetitions"] == 2
    assert result["interval_days"] == 6


def test_third_successful_review_multiplies_by_ease_factor():
    state = ReviewState(interval_days=6, ease_factor=2.5, repetitions=2)
    result = schedule_next_review(quality=5, state=state, reference_date=date(2026, 1, 1))
    assert result["repetitions"] == 3
    assert result["interval_days"] == round(6 * 2.5)


def test_failed_review_resets_repetitions_and_interval():
    state = ReviewState(interval_days=6, ease_factor=2.5, repetitions=2)
    result = schedule_next_review(quality=1, state=state, reference_date=date(2026, 1, 1))
    assert result["repetitions"] == 0
    assert result["interval_days"] == 1


def test_ease_factor_has_lower_bound():
    state = ReviewState(interval_days=1, ease_factor=1.3, repetitions=1)
    result = schedule_next_review(quality=0, state=state, reference_date=date(2026, 1, 1))
    assert result["ease_factor"] >= 1.3


def test_invalid_quality_raises():
    state = ReviewState(interval_days=0, ease_factor=2.5, repetitions=0)
    with pytest.raises(ValueError):
        schedule_next_review(quality=6, state=state)
