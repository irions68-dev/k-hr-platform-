"""LLM이 인용한 법조문/판례가 실제 검색된 근거에 존재하는지 검증한다.

시스템 프롬프트 지침만으로는 LLM이 존재하지 않는 조문 번호를 지어낼 수
있으므로(citation hallucination), 검색된 청크의 인용 라벨과 문자열
대조하여 불일치하는 인용은 제거하고 "행정해석 확인 필요"로 대체한다.
"""
from __future__ import annotations

UNVERIFIED_NOTICE = "행정해석 확인 필요"


def verify_citations(
    cited_references: list[str], retrieved_citations: list[str]
) -> dict:
    verified: list[str] = []
    rejected: list[str] = []

    for ref in cited_references:
        stripped = ref.strip()
        if any(
            stripped in retrieved or retrieved in stripped
            for retrieved in retrieved_citations
        ):
            verified.append(ref)
        else:
            rejected.append(ref)

    final_references = verified if verified else [UNVERIFIED_NOTICE]
    return {
        "verified_references": verified,
        "rejected_references": rejected,
        "final_references": final_references,
    }
