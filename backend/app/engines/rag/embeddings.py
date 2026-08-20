"""Gemini 임베딩 API 래퍼.

원래는 로컬 fastembed(다국어 MiniLM, 모델 약 220MB)를 썼으나, Render 무료
플랜(RAM 512MB)에 배포했을 때 모델을 메모리에 올리는 순간 OOM으로 프로세스가
죽는 걸 실측으로 확인했다(2026-08-02). 이미 생성(generation.py)에 쓰고 있는
Gemini API의 임베딩 엔드포인트로 교체해서 로컬 모델 자체를 없앴다 - 메모리
부담이 사라지고 API 키 하나로 생성+검색을 다 처리한다.

클라이언트 생성·미설정 예외는 `gemini_client.py`에 공용으로 모아뒀다. 다만
임베딩은 코퍼스 적재 시 같은 프로세스 안에서 여러 번 연달아 호출되므로,
호출마다 클라이언트를 새로 만들지 않도록 여기서만 별도로 캐시한다.
"""
from __future__ import annotations

from google import genai
from google.genai import errors, types

from app.engines.gemini_client import GeminiNotConfiguredError, GeminiQuotaExceededError
from app.engines.gemini_client import get_client as _get_shared_client

MODEL_NAME = "gemini-embedding-001"

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = _get_shared_client()
    return _client


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """texts를 임베딩한다.

    task_type은 문서 적재 시 RETRIEVAL_DOCUMENT, 질의 검색 시 RETRIEVAL_QUERY로
    구분한다 - Gemini 임베딩 모델이 두 역할을 비대칭으로 인코딩하도록 설계되어
    있어(검색 품질에 실제 영향), 호출부에서 반드시 구분해서 넘겨야 한다.
    """
    try:
        response = _get_client().models.embed_content(
            model=MODEL_NAME,
            contents=texts,
            config=types.EmbedContentConfig(task_type=task_type),
        )
    except errors.ClientError as exc:
        if exc.code == 429:
            raise GeminiQuotaExceededError(
                "Gemini API 사용 한도를 초과했습니다. 잠시 후 다시 시도하거나 "
                "무료 티어 일일 한도라면 내일 다시 시도하세요."
            ) from exc
        raise
    return [e.values for e in response.embeddings]
