from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AssistantRouteRequest(BaseModel):
    text: str = Field(min_length=1)


class AssistantRouteResult(BaseModel):
    category: str
    category_label: str
    result: dict[str, Any]
