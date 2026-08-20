"""잠재 고객사의 현재 아웃소싱 운영 방식을 파견법 조문·판례에 비추어

진단하고, 합법적 도급/파견 모델로 전환 시 이점을 정리한 영업용 리포트를
만든다. 법령 Q&A와 같은 코퍼스(ChromaDB)를 검색해서 근거로 쓰되, 스키마가
달라서(진단+영업피치 vs 단순 Q&A) generation.py를 그대로 재사용하지 않고
gemini_client.generate_structured_json을 직접 쓴다. 인용 검증은
citation_verifier를 그대로 재사용 - 이 리포트가 실제 법적 자문처럼
보이면 위험하므로, 검색되지 않은 조문을 LLM이 지어내지 못하게 막는다.
"""
from __future__ import annotations

from app.engines.gemini_client import generate_structured_json
from app.engines.rag import citation_verifier
from app.engines.rag.vector_store import VectorStore, get_default_store

SYSTEM_PROMPT = (
    "너는 인력파견회사 영업 담당자를 돕는 컴플라이언스 진단 도우미이다. "
    "담당자가 설명한 (잠재)고객사의 현재 아웃소싱/도급 운영 방식을 "
    "[검색된 근거 조문 및 판례]에 비추어 진단하라. "
    "risk_level에는 위장도급·불법파견 리스크 수준을 '높음', '주의', '낮음' "
    "중 하나로 판단해서 담아라. "
    "risk_summary에는 그렇게 판단한 근거를 검색된 조문·판례를 반드시 인용하여 "
    "설명하라. 검색된 근거로 뒷받침되지 않는 내용은 추측하지 말고 "
    "'단정하기 어려움'을 명시하라. "
    "legal_references에는 risk_summary에서 실제로 인용한 조문·판례 표기만 "
    "정확히 담아라(존재하지 않는 조문 번호를 지어내지 마라). "
    "pitch에는 이 진단 결과를 바탕으로 고객사에게 우리 회사(합법적 도급/파견 "
    "운영 모델)로 전환할 경우의 이점을 전문적이고 설득력 있게, 과장 없이 "
    "작성하라. "
    "risk_summary 끝에는 이 리포트가 실제 법적 자문이 아니라 영업 참고용 "
    "초안이며 최종 판단은 노무사·변호사 등 전문가 확인이 필요하다는 점을 "
    "반드시 명시하라."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_level": {"type": "string", "enum": ["높음", "주의", "낮음"]},
        "risk_summary": {"type": "string"},
        "legal_references": {"type": "array", "items": {"type": "string"}},
        "pitch": {"type": "string"},
    },
    "required": ["risk_level", "risk_summary", "legal_references", "pitch"],
}

_NOT_FOUND_RESULT = {
    "risk_level": "판단 불가",
    "risk_summary": (
        "관련 근거 조문·판례를 찾지 못했습니다. 노무사 등 전문가 확인이 필요합니다."
    ),
    "legal_references": [citation_verifier.UNVERIFIED_NOTICE],
    "pitch": "",
}


def check_compliance(situation: str, store: VectorStore | None = None) -> dict:
    store = store or get_default_store()

    results = store.query(situation, top_k=3)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    retrieved_citations = [m["citation"] for m in metadatas]

    if not documents:
        return dict(_NOT_FOUND_RESULT)

    context = "\n\n".join(documents)
    prompt = f"[검색된 근거 조문 및 판례]\n{context}\n\n[고객사 운영 방식 설명]\n{situation}"

    raw = generate_structured_json(prompt, SYSTEM_PROMPT, RESPONSE_SCHEMA)
    verification = citation_verifier.verify_citations(
        raw.get("legal_references", []), retrieved_citations
    )

    return {
        "risk_level": raw.get("risk_level", ""),
        "risk_summary": raw.get("risk_summary", ""),
        "legal_references": verification["final_references"],
        "pitch": raw.get("pitch", ""),
    }
