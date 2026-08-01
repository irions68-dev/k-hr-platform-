"""검색(retrieval) → 생성(generation) → 인용 검증까지 이어지는 RAG 파이프라인."""
from __future__ import annotations

from app.engines.rag import citation_verifier, generation
from app.engines.rag.vector_store import VectorStore, get_default_store


def ask(question: str, top_k: int = 3, store: VectorStore | None = None) -> dict:
    store = store or get_default_store()

    results = store.query(question, top_k=top_k)
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    retrieved_citations = [m["citation"] for m in metadatas]

    if not documents:
        return {
            "answer": "관련 근거를 찾지 못했습니다. 행정해석 확인 필요.",
            "legal_references": [citation_verifier.UNVERIFIED_NOTICE],
            "rejected_references": [],
            "study_tag": None,
            "retrieved_citations": [],
        }

    raw = generation.generate_grounded_answer(question, documents)
    verification = citation_verifier.verify_citations(
        raw.get("legal_references", []), retrieved_citations
    )

    return {
        "answer": raw.get("answer", ""),
        "legal_references": verification["final_references"],
        "rejected_references": verification["rejected_references"],
        "study_tag": raw.get("study_tag"),
        "retrieved_citations": retrieved_citations,
    }
