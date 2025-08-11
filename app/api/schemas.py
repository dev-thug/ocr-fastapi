from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


class APIError(BaseModel):
    code: str = Field(default="BadRequest")
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class StandardResponse(BaseModel):
    success: bool
    result: Optional[dict[str, Any]] = None
    error: Optional[APIError] = None
    meta: dict[str, Any] = Field(default_factory=dict)


def ok(result: dict[str, Any] | None = None, meta: dict[str, Any] | None = None) -> StandardResponse:
    return StandardResponse(success=True, result=result or {}, error=None, meta=meta or {})


def fail(code: str, message: str, details: dict[str, Any] | None = None, meta: dict[str, Any] | None = None) -> StandardResponse:
    return StandardResponse(success=False, result=None, error=APIError(code=code, message=message, details=details or {}), meta=meta or {})
