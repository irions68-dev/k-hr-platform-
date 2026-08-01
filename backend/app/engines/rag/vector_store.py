"""ChromaDB 로컬 영속 벡터 스토어.

Pinecone 같은 유료 클라우드 벡터DB 대신 로컬 파일 모드로 충분하다
(1인용, 트래픽이 사실상 본인 1명뿐).
"""
from __future__ import annotations

from pathlib import Path

import chromadb

from app.engines.rag.embeddings import embed_texts

DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent.parent.parent / "chroma_db"
COLLECTION_NAME = "legal_documents"


class VectorStore:
    def __init__(
        self, persist_dir: Path | None = None, collection_name: str = COLLECTION_NAME
    ) -> None:
        self.persist_dir = persist_dir or DEFAULT_DB_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_documents(
        self, ids: list[str], texts: list[str], metadatas: list[dict]
    ) -> None:
        embeddings = embed_texts(texts)
        self.collection.upsert(
            ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas
        )

    def query(self, query_text: str, top_k: int = 3) -> dict:
        query_embedding = embed_texts([query_text])[0]
        return self.collection.query(query_embeddings=[query_embedding], n_results=top_k)

    def count(self) -> int:
        return self.collection.count()


_default_store: VectorStore | None = None


def get_default_store() -> VectorStore:
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store
