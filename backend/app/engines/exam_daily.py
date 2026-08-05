"""매일 기출문제 3개 선정 + 채점 엔진.

기존 수험학습(spaced_repetition.py, SM-2)을 그대로 재사용한다 - 오늘
복습 예정인 문항을 우선 채우고, 부족하면 아직 안 푼 신규 문항 중
중요도(High 우선)·최신 연도 순으로 채운다. 맞히거나 확신도가 높으면
간격이 늘어나 자연스럽게 로테이션되고, 틀리거나 확신이 낮으면 금방
다시 나온다.
"""
from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path

from sqlalchemy.orm import Session

from app.engines import spaced_repetition
from app.models.exam_question_progress import ExamQuestionProgress

QUESTIONS_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "exam_questions.json"
)

IMPORTANCE_RANK = {"High": 0, "Medium": 1, "Low": 2}


@lru_cache(maxsize=1)
def load_question_bank() -> dict[str, dict]:
    with QUESTIONS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return {q["id"]: q for q in data["questions"]}


def _public_view(question: dict) -> dict:
    return {
        "id": question["id"],
        "subject": question["subject"],
        "number": question["number"],
        "question": question["question"],
        "choices": question["choices"],
    }


def select_daily_questions(db: Session, count: int = 3) -> list[dict]:
    bank = load_question_bank()
    today = date.today()

    progress_by_id = {
        p.question_id: p for p in db.query(ExamQuestionProgress).all()
    }

    due = [
        (progress_by_id[qid], bank[qid])
        for qid in bank
        if qid in progress_by_id and progress_by_id[qid].next_review_date <= today
    ]
    due.sort(key=lambda pair: (pair[0].next_review_date, IMPORTANCE_RANK.get(pair[1]["importance"], 1)))

    selected_ids = [q["id"] for _, q in due[:count]]

    if len(selected_ids) < count:
        unseen = [
            bank[qid] for qid in bank if qid not in progress_by_id and qid not in selected_ids
        ]
        unseen.sort(key=lambda q: IMPORTANCE_RANK.get(q["importance"], 1))
        for q in unseen:
            if len(selected_ids) >= count:
                break
            selected_ids.append(q["id"])

    if len(selected_ids) < count:
        # 문제은행을 다 돌았으면 가장 오래전에 본 문항부터 다시 채운다
        seen = sorted(
            (p for p in progress_by_id.values() if p.question_id not in selected_ids),
            key=lambda p: p.next_review_date,
        )
        for p in seen:
            if len(selected_ids) >= count:
                break
            selected_ids.append(p.question_id)

    return [_public_view(bank[qid]) for qid in selected_ids]


def record_attempt(db: Session, question_id: str, selected_index: int) -> dict:
    """객관식이라 정오가 자동으로 갈리므로, SM-2에 넘길 quality도 정답 여부에서
    바로 끌어낸다(맞으면 5, 틀리면 1) - 별도 확신도 입력 단계를 두지 않는다.
    """
    bank = load_question_bank()
    question = bank.get(question_id)
    if question is None:
        raise ValueError(f"알 수 없는 문항 ID: {question_id}")

    correct = selected_index == question["answer_index"]
    quality = 5 if correct else 1

    progress = (
        db.query(ExamQuestionProgress)
        .filter(ExamQuestionProgress.question_id == question_id)
        .first()
    )
    if progress is None:
        progress = ExamQuestionProgress(
            question_id=question_id,
            next_review_date=date.today(),
            interval_days=0,
            ease_factor=spaced_repetition.DEFAULT_EASE_FACTOR,
            repetitions=0,
            times_shown=0,
            times_correct=0,
        )
        db.add(progress)

    result = spaced_repetition.schedule_next_review(
        quality=quality,
        state=spaced_repetition.ReviewState(
            interval_days=progress.interval_days,
            ease_factor=progress.ease_factor,
            repetitions=progress.repetitions,
        ),
    )
    progress.interval_days = result["interval_days"]
    progress.ease_factor = result["ease_factor"]
    progress.repetitions = result["repetitions"]
    progress.next_review_date = result["next_review_date"]
    progress.times_shown += 1
    progress.times_correct += 1 if correct else 0
    db.commit()

    return {
        "correct": correct,
        "answer_index": question["answer_index"],
        "explanation": question.get("explanation"),
        "keywords": question.get("keywords", []),
        "next_review_date": progress.next_review_date,
    }


def get_stats(db: Session) -> dict:
    bank = load_question_bank()
    progresses = db.query(ExamQuestionProgress).all()
    total_shown = sum(p.times_shown for p in progresses)
    total_correct = sum(p.times_correct for p in progresses)
    return {
        "total_questions": len(bank),
        "attempted_questions": len(progresses),
        "total_attempts": total_shown,
        "total_correct": total_correct,
        "accuracy": round(total_correct / total_shown, 3) if total_shown else None,
    }
