"""개인 실무 사례 히스토리 아카이브.

참고: 현재 검색은 SQL LIKE 기반 키워드 매칭이다. 법령/판례 RAG처럼
임베딩 기반 의미 검색으로 확장하려면 별도 벡터DB + 임베딩 API 키가
필요하므로 지금은 범위에서 제외한다.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.case_note import REFERENCE_SEPARATOR, CaseNote
from app.schemas.case_note import CaseNoteCreate, CaseNoteOut

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseNoteOut)
def create_case(payload: CaseNoteCreate, db: Session = Depends(get_db)) -> dict:
    case = CaseNote(
        question=payload.question,
        answer=payload.answer,
        legal_references=REFERENCE_SEPARATOR.join(payload.legal_references),
        exam_part=payload.exam_part,
        core_keyword=payload.core_keyword,
        importance=payload.importance,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return _to_out(case)


@router.get("/search", response_model=list[CaseNoteOut])
def search_cases(q: str = "", db: Session = Depends(get_db)) -> list[dict]:
    query = db.query(CaseNote)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                CaseNote.question.like(like),
                CaseNote.answer.like(like),
                CaseNote.core_keyword.like(like),
            )
        )
    cases = query.order_by(CaseNote.created_at.desc()).all()
    return [_to_out(c) for c in cases]


def _to_out(case: CaseNote) -> dict:
    return {
        "id": case.id,
        "question": case.question,
        "answer": case.answer,
        "legal_references": (
            case.legal_references.split(REFERENCE_SEPARATOR)
            if case.legal_references
            else []
        ),
        "exam_part": case.exam_part,
        "core_keyword": case.core_keyword,
        "importance": case.importance,
        "created_at": case.created_at,
    }
