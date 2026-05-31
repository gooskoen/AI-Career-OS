# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class PaginatedResponse(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total: int = Field(ge=0)


def success_response(data: T) -> dict:
    return {"success": True, "data": data}


def paginated_response(
    data: list[T],
    *,
    page: int,
    page_size: int,
    total: int,
) -> dict:
    return {
        "success": True,
        "data": data,
        "page": page,
        "page_size": page_size,
        "total": total,
    }
