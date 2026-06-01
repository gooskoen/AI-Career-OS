# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, TypeVar

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg import Error as PsycopgError

from app.auth import decode_access_token
from app.database import get_connection
from app.ingestion import IngestionError, UrlFetchError
from app.repositories import get_user

T = TypeVar("T")
bearer_scheme = HTTPBearer(auto_error=False)


def example_profile_path() -> Path:
    configured_path = os.getenv("EXAMPLE_PROFILE_PATH")
    if configured_path:
        return Path(configured_path)

    candidates = [
        Path.cwd() / "examples" / "candidate_profile.example.json",
        Path(__file__).resolve().parents[1] / "examples" / "candidate_profile.example.json",
        Path(__file__).resolve().parents[2] / "examples" / "candidate_profile.example.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def run_database_operation(operation: Callable[..., T]) -> T:
    try:
        with get_connection() as connection:
            return operation(connection)
    except IngestionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UrlFetchError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except PsycopgError as exc:
        raise HTTPException(status_code=503, detail="Database operation failed") from exc


def require_row(row: dict | None, message: str) -> dict:
    if row is None:
        raise HTTPException(status_code=404, detail=message)
    return row


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = run_database_operation(lambda connection: get_user(connection, user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user
