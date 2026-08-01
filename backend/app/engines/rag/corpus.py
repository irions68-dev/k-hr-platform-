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


def ingest_sample_corpus(store: VectorStore | None = None) -> int:
    store = store or get_default_store()
    documents = load_sample_corpus()

    ids = [d["id"] for d in documents]
    texts = [f"{citation_label(d)} ({d['title']}): {d['text']}" for d in documents]
    metadatas = [
        {
            "law_name": d["law_name"],
            "article": d["article"],
            "title": d["title"],
            "citation": citation_label(d),
        }
        for d in documents
    ]

    store.add_documents(ids=ids, texts=texts, metadatas=metadatas)
    return len(documents)
