"""이력서 스캔본/촬영본을 Gemini Vision으로 읽어 구조화된 필드로 뽑아낸다.

계산기들과 같은 "즉시 처리, 저장 안 함" 원칙 - 후보자 DB를 새로 만들면
회사 채용 플랫폼과 기능이 겹치므로(파견근로자 DB를 들어냈던 것과 같은
이유), 여기서는 화면에 구조화해서 보여주고 복사하는 용도로만 쓴다.

클라이언트 생성·429/미설정 예외·JSON 파싱은 `gemini_client.py`에 공용으로
모아뒀다(법령 Q&A의 generation.py와 공유).
"""
from __future__ import annotations

from google.genai import types

from app.engines.gemini_client import (
    GeminiNotConfiguredError,
    GeminiQuotaExceededError,
    generate_structured_json,
)

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}

SYSTEM_PROMPT = (
    "너는 인력파견회사 채용 담당자를 돕는 이력서 판독 도우미이다. "
    "첨부된 이력서 이미지/문서에서 정보를 읽어 지정된 JSON 스키마로만 응답하라. "
    "문서에 실제로 적힌 내용만 추출하고, 확인되지 않는 항목은 빈 문자열이나 빈 배열로 "
    "남겨두어라(추측하여 채우지 말 것). "
    "주민등록번호는 절대 출력하지 마라 - 문서에 보이더라도 완전히 무시하고 "
    "어떤 필드에도 포함시키지 마라. "
    "career 항목은 최근 경력이 배열의 앞쪽에 오도록 정렬하고, "
    "total_years_experience는 career 항목들의 재직기간을 합산해 추정한 총 경력 연차이다 "
    "(신입이거나 경력이 없으면 0). "
    "사용자 메시지에 [고객사 직무조건]이 포함되어 있으면, 이력서 내용이 그 조건에 "
    "얼마나 부합하는지 100점 만점으로 채점해서 match_score에 담고, "
    "match_strengths에는 부합하는 강점을 2~3개, match_concerns에는 우려되는 점이나 "
    "부족한 부분을 1~2개 짧은 문장으로 담아라(부족한 점이 없으면 빈 배열). "
    "[고객사 직무조건]이 없으면 match_score는 0, match_strengths와 match_concerns는 "
    "빈 배열로 남겨라(채점하지 마라)."
)

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "birth_date": {"type": "string"},
        "phone": {"type": "string"},
        "email": {"type": "string"},
        "address": {"type": "string"},
        "total_years_experience": {"type": "number"},
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "school": {"type": "string"},
                    "major": {"type": "string"},
                    "degree": {"type": "string"},
                    "status": {"type": "string"},
                },
                "required": ["school"],
            },
        },
        "career": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {"type": "string"},
                    "period": {"type": "string"},
                    "role": {"type": "string"},
                },
                "required": ["company"],
            },
        },
        "certifications": {"type": "array", "items": {"type": "string"}},
        "languages": {"type": "array", "items": {"type": "string"}},
        "military_service": {"type": "string"},
        "desired_position": {"type": "string"},
        "desired_salary": {"type": "string"},
        "desired_location": {"type": "string"},
        "notes": {"type": "string"},
        "match_score": {"type": "number"},
        "match_strengths": {"type": "array", "items": {"type": "string"}},
        "match_concerns": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "name",
        "phone",
        "email",
        "total_years_experience",
        "education",
        "career",
        "certifications",
        "match_score",
        "match_strengths",
        "match_concerns",
    ],
}


class UnsupportedFileTypeError(ValueError):
    pass


class FileTooLargeError(ValueError):
    pass


def extract_resume(file_bytes: bytes, mime_type: str, job_description: str = "") -> dict:
    if mime_type not in ALLOWED_MIME_TYPES:
        raise UnsupportedFileTypeError(
            f"지원하지 않는 파일 형식입니다: {mime_type} "
            f"(지원: {', '.join(sorted(ALLOWED_MIME_TYPES))})"
        )
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileTooLargeError("파일 크기가 10MB를 초과합니다.")

    job_description = job_description.strip()
    if job_description:
        prompt = (
            f"[고객사 직무조건]\n{job_description}\n\n"
            "첨부된 이력서에서 정보를 추출하고, 위 직무조건에 얼마나 부합하는지도 평가해줘."
        )
    else:
        prompt = "첨부된 이력서에서 정보를 추출해줘."

    contents = [types.Part.from_bytes(data=file_bytes, mime_type=mime_type), prompt]
    return generate_structured_json(contents, SYSTEM_PROMPT, RESPONSE_SCHEMA)
