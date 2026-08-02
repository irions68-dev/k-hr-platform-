"""샘플 법령 코퍼스를 벡터 스토어에 적재.

app/data/sample_legal_corpus.json은 파이프라인 검증용 샘플이며,
실사용 전 국가법령정보센터 원문으로 교체해야 한다.
"""
from __future__ import annotations

import json
from pathlib import Path

from app.engines.rag.vector_store import VectorStore, get_default_store

CORPUS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "sample_legal_corpus.json"
)


def load_sample_corpus() -> list[dict]:
    with CORPUS_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["documents"]


def citation_label(document: dict) -> str:
    return f"{document['law_name']} {document['article']}"


def _embedding_text(document: dict) -> str:
    """검색(임베딩) 전용 짧은 텍스트를 만든다.

    실측 결과 일반 다국어 임베딩 모델(fastembed MiniLM)은 법률 전문용어
    간 미묘한 차이(예: "위장도급" vs "근로자성")를 잘 구분하지 못해서,
    핵심 키워드가 긴 본문 중간에 묻히면 검색 순위에서 밀리는 문제가
    확인됐다. 그래서 임베딩용 텍스트는 키워드+제목만으로 짧고 밀도
    높게 만들고(키워드 2회 반복으로 신호 강화), LLM에 전달할 본문은
    add_documents()의 texts(=전체 조문/판례 원문)로 별도 유지한다.
    """
    keywords = document.get("keywords", [])
    keyword_str = ", ".join(keywords)
    return f"{keyword_str}. {document['title']}. {keyword_str}"


def ingest_sample_corpus(store: VectorStore | None = None) -> int:
    store = store or get_default_store()
    documents = load_sample_corpus()

    ids = [d["id"] for d in documents]
    texts = [
        f"{citation_label(d)} ({d['title']}): {d['text']}" for d in documents
    ]
    embedding_texts = [_embedding_text(d) for d in documents]
    metadatas = [
        {
            "law_name": d["law_name"],
            "article": d["article"],
            "title": d["title"],
            "citation": citation_label(d),
        }
        for d in documents
    ]

    store.add_documents(
        ids=ids, texts=texts, metadatas=metadatas, embedding_texts=embedding_texts
    )
    return len(documents)
