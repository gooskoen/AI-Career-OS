# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import base64
import hashlib
import hmac
import importlib.util
import json
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.auth import (
    auth_secret,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.application_domain import ApplicationNoteRequest
from app.dependencies import current_user
from app.errors import _code_for_status
from app.feedback import OutcomeRequest
from app.main import app
from app.matching import MatchResult
from app.repositories.applications import create_application_note, get_application
from app.repositories.candidates import get_candidate
from app.repositories.matching import create_match_result, list_match_results
from app.repositories.outcomes import create_application_outcome, list_application_outcomes


def test_auth_migration_exists_and_adds_ownership() -> None:
    migration_path = Path("migrations/versions/0003_auth_ownership.py")
    assert migration_path.exists()

    spec = importlib.util.spec_from_file_location("auth_migration", migration_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    source = migration_path.read_text()
    assert module.revision == "0003_auth_ownership"
    assert "CREATE TABLE IF NOT EXISTS users" in source
    assert "ALTER TABLE candidate_profiles" in source
    assert "ALTER TABLE applications" in source
    assert "ALTER TABLE match_results" in source


def test_password_hashing_and_jwt_validation_are_deterministic() -> None:
    user_id = uuid4()
    password_hash = hash_password("very-secure-demo-password")
    token = create_access_token(user_id)

    assert verify_password("very-secure-demo-password", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False
    assert decode_access_token(token) == user_id
    assert decode_access_token(token + "tampered") is None


def test_missing_auth_secret_fails_outside_test_mode(monkeypatch) -> None:
    monkeypatch.delenv("AUTH_SECRET", raising=False)

    with pytest.raises(RuntimeError, match="AUTH_SECRET must be configured"):
        auth_secret()


def test_malformed_jwt_tokens_return_normalized_401() -> None:
    client = TestClient(app)
    tokens = [
        _signed_token("a"),
        _signed_token(_base64url(b"\xff")),
        _signed_token(_base64url(b"not-json")),
    ]

    for token in tokens:
        response = client.get(
            "/applications",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "authentication_error"


def test_error_codes_distinguish_authentication_and_authorization() -> None:
    assert _code_for_status(401) == "authentication_error"
    assert _code_for_status(403) == "authorization_error"


def test_register_endpoint_returns_tokens_without_password_hash(monkeypatch) -> None:
    user_id = uuid4()

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_get_user_by_email(connection, email):
        assert email == "demo@example.com"
        return None

    def fake_create_user(connection, *, email, display_name, password_hash):
        assert email == "demo@example.com"
        assert display_name == "Demo User"
        assert "plain-text-password" not in password_hash
        return {
            "id": user_id,
            "email": email,
            "display_name": display_name,
        }

    import app.routers.auth as auth_router

    monkeypatch.setattr(auth_router, "run_database_operation", fake_run_database_operation)
    monkeypatch.setattr(auth_router, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_router, "create_user", fake_create_user)
    monkeypatch.setattr(
        auth_router,
        "create_refresh_token_record",
        lambda *args, **kwargs: {},
    )

    response = TestClient(app).post(
        "/auth/register",
        json={
            "email": "demo@example.com",
            "display_name": "Demo User",
            "password": "plain-text-password",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    assert "refresh_token" in body
    assert "password_hash" not in body["user"]


def test_login_and_refresh_endpoints_issue_access_tokens(monkeypatch) -> None:
    user_id = uuid4()
    password_hash = hash_password("very-secure-demo-password")
    refresh_token, refresh_hash, _ = create_refresh_token()
    user = {
        "id": user_id,
        "email": "demo@example.com",
        "display_name": "Demo User",
        "password_hash": password_hash,
    }

    def fake_run_database_operation(operation):
        return operation(object())

    import app.routers.auth as auth_router

    monkeypatch.setattr(auth_router, "run_database_operation", fake_run_database_operation)
    monkeypatch.setattr(auth_router, "get_user_by_email", lambda connection, email: user)
    monkeypatch.setattr(auth_router, "create_auth_audit_event", lambda *args: {})
    monkeypatch.setattr(
        auth_router,
        "create_refresh_token_record",
        lambda *args, **kwargs: {},
    )

    client = TestClient(app)
    login_response = client.post(
        "/auth/login",
        json={"email": "demo@example.com", "password": "very-secure-demo-password"},
    )

    assert login_response.status_code == 200
    assert decode_access_token(login_response.json()["access_token"]) == user_id

    monkeypatch.setattr(
        auth_router,
        "get_refresh_token_record",
        lambda connection, token_hash: (
            {"user_id": user_id} if token_hash == refresh_hash else None
        ),
    )
    monkeypatch.setattr(auth_router, "get_user", lambda connection, target_id: user)

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 200
    assert decode_access_token(refresh_response.json()["access_token"]) == user_id
    assert "password_hash" not in refresh_response.json()["user"]


def test_persisted_match_listing_is_scoped_by_user() -> None:
    user_id = uuid4()
    connection = FakeConnection([])

    list_match_results(connection, user_id)

    assert "WHERE user_id = %s" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params == (user_id,)


def test_cross_user_candidate_access_returns_none() -> None:
    user_id = uuid4()
    candidate_id = uuid4()
    connection = FakeConnection([None])

    assert get_candidate(connection, candidate_id, user_id) is None
    assert "WHERE id = %s" in connection.cursor_obj.last_query
    assert "AND user_id = %s" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params == (candidate_id, user_id)


def test_cross_user_application_access_returns_not_found(monkeypatch) -> None:
    user_id = uuid4()
    application_id = uuid4()

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_get_application(connection, target_application_id, target_user_id):
        assert target_application_id == application_id
        assert target_user_id == user_id
        return None

    import app.routers.applications as applications_router

    monkeypatch.setattr(
        applications_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(applications_router, "get_application", fake_get_application)

    app.dependency_overrides[current_user] = lambda: {
        "id": user_id,
        "email": "demo@example.com",
    }
    response = TestClient(app).get(f"/applications/{application_id}")
    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_cross_user_application_note_creation_returns_none() -> None:
    user_id = uuid4()
    application_id = uuid4()
    connection = FakeConnection([None])

    row = create_application_note(
        connection,
        application_id,
        ApplicationNoteRequest(note="Prepare interview examples."),
        user_id,
    )

    assert row is None
    assert "WHERE EXISTS" in connection.cursor_obj.last_query
    assert "AND user_id = %s" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params[-1] == user_id


def test_cross_user_outcome_creation_returns_none() -> None:
    user_id = uuid4()
    application_id = uuid4()
    connection = FakeConnection([None])

    row = create_application_outcome(
        connection,
        OutcomeRequest(
            candidate_id=uuid4(),
            job_id=uuid4(),
            application_id=application_id,
            outcome="applied",
            notes="Applied.",
        ),
        user_id,
    )

    assert row is None
    assert "WHERE EXISTS" in connection.cursor_obj.last_query
    assert "AND user_id = %s" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params[-1] == user_id


def test_cross_user_outcome_history_returns_empty() -> None:
    user_id = uuid4()
    candidate_id = uuid4()
    connection = FakeConnection([])

    assert list_application_outcomes(connection, candidate_id, user_id) == []
    assert "AND user_id = %s" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params == (candidate_id, user_id)


def test_cannot_create_match_result_for_other_users_candidate() -> None:
    user_id = uuid4()
    candidate_id = uuid4()
    connection = FakeConnection([None])

    row = create_match_result(
        connection,
        candidate_id,
        uuid4(),
        MatchResult(
            score=80,
            matched_keywords=["python"],
            missing_keywords=[],
            candidate_highlights=[],
            recommendation="Proceed.",
        ),
        user_id,
    )

    assert row is None
    assert "FROM candidate_profiles" in connection.cursor_obj.last_query
    assert "AND user_id = %s" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params[-2:] == (candidate_id, user_id)


def test_private_repositories_reject_missing_user_id() -> None:
    connection = FakeConnection([])

    with pytest.raises(ValueError):
        get_candidate(connection, uuid4(), None)

    with pytest.raises(ValueError):
        get_application(connection, uuid4(), None)

    with pytest.raises(ValueError):
        list_match_results(connection, None)

    with pytest.raises(ValueError):
        list_application_outcomes(connection, uuid4(), None)


def _signed_token(payload_segment: str) -> str:
    header_segment = _base64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = base64.urlsafe_b64encode(
        hmac.new(auth_secret(), signing_input, hashlib.sha256).digest()
    ).rstrip(b"=").decode("ascii")
    return f"{header_segment}.{payload_segment}.{signature}"


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


class FakeConnection:
    def __init__(self, results):
        self.cursor_obj = FakeCursor(results)

    def cursor(self):
        return self.cursor_obj


class FakeCursor:
    def __init__(self, results):
        self.results = list(results)
        self.last_query = ""
        self.last_params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params

    def fetchall(self):
        return self.results

    def fetchone(self):
        if not self.results:
            return None
        return self.results.pop(0)
