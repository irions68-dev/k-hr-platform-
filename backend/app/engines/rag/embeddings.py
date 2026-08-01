"""로컬 오픈소스 임베딩 모델 래퍼.

1인용 로컬 도구이므로 API 키/토큰 비용이 드는 임베딩 API 대신
다국어 지원 오픈소스 모델을 로컬에서 실행한다. 모델 캐시는 알약 등
실시간 백신 검사 대상이 되기 쉬운 시스템 임시폴더를 피해 프로젝트
하위 .cache 디렉토리에 저장한다.
"""
from __future__ import annotations

from pathlib import Path

from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CACHE_DIR = Path(__file__).resolve().parent.parent.parent.parent / ".cache" / "fastembed"

_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR))
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    return [vec.tolist() for vec in _get_model().embed(texts)]
