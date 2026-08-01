"""1인용 도구를 위한 최소한의 인증.

RBAC나 세션 관리 같은 복잡한 구조 대신, 환경변수(APP_PASSWORD)에 설정한
비밀번호를 요청 헤더로 대조하는 미들웨어 하나로 충분하다. APP_PASSWORD가
설정되지 않으면(개발 중) 인증을 건너뛰고 경고만 남긴다.
"""
from __future__ import annotations

import os
import warnings

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

AUTH_HEADER = "X-App-Password"
EXEMPT_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


class SharedPasswordAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        password = os.environ.get("APP_PASSWORD")
        if not password:
            return await call_next(request)

        if request.method == "OPTIONS" or request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        if request.headers.get(AUTH_HEADER) != password:
            return JSONResponse(
                status_code=401, content={"detail": "인증이 필요합니다."}
            )

        return await call_next(request)


def warn_if_auth_disabled() -> None:
    if not os.environ.get("APP_PASSWORD"):
        warnings.warn(
            "APP_PASSWORD 환경변수가 설정되지 않아 인증 없이 실행됩니다. "
            "로컬 개발 외 환경에서는 반드시 설정하세요.",
            stacklevel=2,
        )
