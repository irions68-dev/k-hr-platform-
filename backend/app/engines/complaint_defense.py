"""근로자가 보낸 감정적/공격적 민원 텍스트를 그대로 입력하면, 감정을 배제한

사무적 방어 답변과 근거 조항, 매니저 내부 유의사항을 만들어준다.
compliance_check.py와 거의 동일한 구조(같은 ChromaDB 코퍼스를 검색해서
근거로 쓰고, 검색되지 않은 조문은 지어내지 못하게 citation_verifier로
막는다) - 스키마만 다르다.
"""
from __future__ import annotations

from app.engines.gemini_client import generate_structured_json
from app.engines.rag import citation_verifier
from app.engines.rag.vector_store import VectorStore, get_default_store

SYSTEM_PROMPT = (
    "너는 15년 차 베테랑 노무사이자 냉철한 대기업 법무팀장이다. "
    "인력파견회사의 현장 관리 매니저가 근로자로부터 받은 감정적이거나 "
    "공격적인 민원·항의 텍스트를 [검색된 근거 조문 및 판례]에 비추어 "
    "차분하고 사무적으로 응대할 수 있도록 돕는다. "
    "defense_response에는 감정적 표현을 완전히 배제한, 극도로 드라이하고 "
    "사무적인 답변 텍스트를 작성하라. 매니저가 그대로 복사해서 근로자에게 "
    "보낼 수 있는 수준이어야 하며, 회사측 주장만 일방적으로 강요하지 말고 "
    "사실관계 확인을 요청하는 정중한 문구도 포함하라. "
    "legal_basis_explanation에는 검색된 조문·판례가 이 상황에 왜 적용되는지 "
    "설명하라. 검색된 근거로 뒷받침되지 않는 내용은 추측하지 말고 "
    "'단정하기 어려움'을 명시하라. "
    "legal_basis에는 legal_basis_explanation에서 실제로 인용한 조문·판례 "
    "표기만 정확히 담아라(존재하지 않는 조문 번호를 지어내지 마라). "
    "caution_note에는 매니저가 내부적으로 유의할 사항(감정적 대응 금지, "
    "대화 녹취 가능성 대비, 노동청 진정 시 준비해야 할 자료 등)을 적고, "
    "끝에는 이 답변이 실제 법적 자문이 아니라 참고용 초안이며 상황이 심각할 "
    "경우 노무사·변호사 확인이 필요하다는 점을 반드시 명시하라."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "defense_response": {"type": "string"},
        "legal_basis": {"type": "array", "items": {"type": "string"}},
        "legal_basis_explanation": {"type": "string"},
        "caution_note": {"type": "string"},
    },
    "required": [
        "defense_response",
        "legal_basis",
        "legal_basis_explanation",
        "caution_note",
    ],
}

_NOT_FOUND_RESULT = {
    "defense_response": "",
    "legal_basis": [citation_verifier.UNVERIFIED_NOTICE],
    "legal_basis_explanation": (
        "관련 근거 조문·판례를 찾지 못했습니다. 노무사 등 전문가 확인이 필요합니다."
    ),
    "caution_note": (
        "감정적으로 대응하지 말고, 사실관계를 먼저 정리한 뒤 노무사와 상의하세요."
    ),
}


def generate_defense(complaint_text: str, store: VectorStore | None = None) -> dict:
    store = store or get_default_store()

    results = store.query(complaint_text, top_k=3)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    retrieved_citations = [m["citation"] for m in metadatas]

    if not documents:
        return dict(_NOT_FOUND_RESULT)

    context = "\n\n".join(documents)
    prompt = f"[검색된 근거 조문 및 판례]\n{context}\n\n[근로자 민원 원문]\n{complaint_text}"

    raw = generate_structured_json(prompt, SYSTEM_PROMPT, RESPONSE_SCHEMA)
    verification = citation_verifier.verify_citations(
        raw.get("legal_basis", []), retrieved_citations
    )

    return {
        "defense_response": raw.get("defense_response", ""),
        "legal_basis": verification["final_references"],
        "legal_basis_explanation": raw.get("legal_basis_explanation", ""),
        "caution_note": raw.get("caution_note", ""),
    }
