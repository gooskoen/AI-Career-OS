# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, TypeVar

from fastapi import HTTPException
from psycopg import Error as PsycopgError

from app.database import get_connection
from app.ingestion import IngestionError, UrlFetchError

T = TypeVar("T")


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
