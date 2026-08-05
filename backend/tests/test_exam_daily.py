from datetime import date, timedelta

from app.engines import exam_daily
from app.models.exam_question_progress import ExamQuestionProgress


def test_load_question_bank_has_required_fields():
    bank = exam_daily.load_question_bank()
    assert len(bank) > 0
    for qid, q in bank.items():
        assert q["id"] == qid
        assert len(q["choices"]) == 5
        assert 1 <= q["answer_index"] <= 5
        assert q["subject"] in {"노동법1", "노동법2", "사회보험법", "민법", "경제학원론", "경영학개론"}


def test_select_daily_questions_returns_three_and_hides_answer(client_db):
    questions = exam_daily.select_daily_questions(client_db, count=3)
    assert len(questions) == 3
    for q in questions:
        assert "answer_index" not in q
        assert "explanation" not in q


def test_select_daily_questions_prioritizes_due_items(client_db):
    bank = exam_daily.load_question_bank()
    some_id = next(iter(bank))
    client_db.add(
        ExamQuestionProgress(
            question_id=some_id,
            next_review_date=date.today() - timedelta(days=1),
            interval_days=1,
            ease_factor=2.5,
            repetitions=1,
        )
    )
    client_db.commit()

    questions = exam_daily.select_daily_questions(client_db, count=3)
    assert any(q["id"] == some_id for q in questions)


def test_record_attempt_correct_answer_advances_schedule(client_db):
    bank = exam_daily.load_question_bank()
    qid, question = next(iter(bank.items()))

    result = exam_daily.record_attempt(client_db, qid, question["answer_index"])

    assert result["correct"] is True
    assert result["answer_index"] == question["answer_index"]
    assert result["next_review_date"] > date.today()

    progress = (
        client_db.query(ExamQuestionProgress)
        .filter(ExamQuestionProgress.question_id == qid)
        .first()
    )
    assert progress.times_shown == 1
    assert progress.times_correct == 1


def test_record_attempt_wrong_answer_resets_repetitions(client_db):
    bank = exam_daily.load_question_bank()
    qid, question = next(iter(bank.items()))
    wrong_index = 1 if question["answer_index"] != 1 else 2

    result = exam_daily.record_attempt(client_db, qid, wrong_index)

    assert result["correct"] is False
    progress = (
        client_db.query(ExamQuestionProgress)
        .filter(ExamQuestionProgress.question_id == qid)
        .first()
    )
    assert progress.repetitions == 0
    assert progress.times_correct == 0


def test_record_attempt_unknown_question_raises(client_db):
    try:
        exam_daily.record_attempt(client_db, "no-such-id", 1)
        assert False, "ValueError를 기대했지만 발생하지 않음"
    except ValueError:
        pass


def test_get_stats_reflects_attempts(client_db):
    bank = exam_daily.load_question_bank()
    qid, question = next(iter(bank.items()))
    exam_daily.record_attempt(client_db, qid, question["answer_index"])

    stats = exam_daily.get_stats(client_db)
    assert stats["total_attempts"] == 1
    assert stats["total_correct"] == 1
    assert stats["accuracy"] == 1.0


def test_exam_api_daily_and_attempt_flow(client):
    daily_resp = client.get("/exam/daily")
    assert daily_resp.status_code == 200
    questions = daily_resp.json()
    assert len(questions) == 3
    assert "answer_index" not in questions[0]

    bank = exam_daily.load_question_bank()
    target = bank[questions[0]["id"]]

    attempt_resp = client.post(
        "/exam/attempts",
        json={"question_id": target["id"], "selected_index": target["answer_index"]},
    )
    assert attempt_resp.status_code == 200
    body = attempt_resp.json()
    assert body["correct"] is True
    assert body["answer_index"] == target["answer_index"]

    stats_resp = client.get("/exam/stats")
    assert stats_resp.status_code == 200
    assert stats_resp.json()["total_attempts"] == 1
