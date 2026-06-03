# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import logging
from contextlib import contextmanager

import psycopg
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.dependencies import run_database_operation
from app.main import DEFAULT_CORS_ORIGINS, app, parse_cors_origins


def test_missing_or_empty_cors_origins_use_local_dev_defaults() -> None:
    assert parse_cors_origins("") == DEFAULT_CORS_ORIGINS.copy()
    assert parse_cors_origins("   ") == DEFAULT_CORS_ORIGINS.copy()


def test_cors_origins_parse_comma_separated_values() -> None:
    origins = parse_cors_origins(
        "http://localhost:3000, http://127.0.0.1:3000, http://192.168.1.130:3000"
    )

    assert origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.130:3000",
    ]


def test_auth_register_preflight_allows_configured_frontend_origin() -> None:
    response = TestClient(app).options(
        "/auth/register",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]


def test_auth_register_response_includes_cors_for_allowed_origin(monkeypatch) -> None:
    import app.routers.auth as auth_router

    monkeypatch.setattr(
        auth_router,
        "run_database_operation",
        lambda operation: (_ for _ in ()).throw(
            HTTPException(status_code=409, detail="Email is already registered")
        ),
    )

    response = TestClient(app).post(
        "/auth/register",
        headers={"Origin": "http://localhost:3000"},
        json={
            "email": "demo@example.com",
            "display_name": "Demo User",
            "password": "very-secure-demo-password",
        },
    )

    assert response.status_code == 409
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_disallowed_origin_does_not_receive_permissive_cors() -> None:
    response = TestClient(app).options(
        "/auth/register",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.headers.get("access-control-allow-origin") is None


def test_database_operation_failure_is_logged_without_api_detail_leak(
    monkeypatch,
    caplog,
) -> None:
    @contextmanager
    def fake_connection():
        raise psycopg.Error("users table does not exist")
        yield

    import app.dependencies as dependencies

    monkeypatch.setattr(dependencies, "get_connection", fake_connection)

    with caplog.at_level(logging.ERROR, logger="app.dependencies"):
        with pytest.raises(HTTPException) as exc_info:
            run_database_operation(lambda connection: {"ok": True})

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Database operation failed"
    assert "Database operation failed" in caplog.text
    assert "users table does not exist" in caplog.text
