from datetime import date, timedelta

from app.engines import wellbeing
from app.models.case_note import CaseNote
from app.models.mood_checkin import MoodCheckin


def test_get_today_summary_defaults_when_no_checkin(client_db):
    summary = wellbeing.get_today_summary(client_db)
    assert summary["mood_today"] is None
    assert summary["streak_days"] == 0
    assert summary["quote"]


def test_record_mood_sets_today_checkin(client_db):
    wellbeing.record_mood(client_db, "good", "오늘은 순조로워요")
    summary = wellbeing.get_today_summary(client_db)
    assert summary["mood_today"] == "good"
    assert summary["mood_note"] == "오늘은 순조로워요"
    assert summary["mood_response"]
    assert summary["streak_days"] == 1


def test_record_mood_upserts_same_day(client_db):
    wellbeing.record_mood(client_db, "tired")
    wellbeing.record_mood(client_db, "stressed", "바빴어요")
    summary = wellbeing.get_today_summary(client_db)
    assert summary["mood_today"] == "stressed"
    assert (
        client_db.query(MoodCheckin).count() == 1
    )  # 하루에 하나만 남아야 함(덮어쓰기)


def test_record_mood_rejects_unknown_value(client_db):
    try:
        wellbeing.record_mood(client_db, "excited")
        assert False, "ValueError를 기대했지만 발생하지 않음"
    except ValueError:
        pass


def test_streak_counts_consecutive_days(client_db):
    today = date.today()
    client_db.add(MoodCheckin(checkin_date=today - timedelta(days=2), mood="good"))
    client_db.add(MoodCheckin(checkin_date=today - timedelta(days=1), mood="okay"))
    client_db.commit()

    summary = wellbeing.get_today_summary(client_db)
    assert summary["streak_days"] == 2  # 오늘은 아직 체크인 안 함

    wellbeing.record_mood(client_db, "great")
    summary = wellbeing.get_today_summary(client_db)
    assert summary["streak_days"] == 3


def test_streak_breaks_on_gap(client_db):
    today = date.today()
    client_db.add(MoodCheckin(checkin_date=today - timedelta(days=5), mood="good"))
    client_db.commit()

    summary = wellbeing.get_today_summary(client_db)
    assert summary["streak_days"] == 0


def test_today_counts_reflect_cases_created_today(client_db):
    client_db.add(CaseNote(question="Q", answer="A"))
    client_db.commit()

    summary = wellbeing.get_today_summary(client_db)
    assert summary["cases_today"] == 1


def test_wellbeing_api_round_trip(client):
    resp = client.get("/wellbeing/today")
    assert resp.status_code == 200
    assert resp.json()["mood_today"] is None

    resp = client.post("/wellbeing/mood", json={"mood": "good", "note": "무난"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["mood_today"] == "good"
    assert body["streak_days"] == 1
