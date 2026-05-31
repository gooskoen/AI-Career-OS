# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import importlib.util
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.application_domain import ApplicationNoteRequest
from app.main import app
from app.responses import PaginatedResponse, SuccessResponse, paginated_response
from app.schemas import JobImportTextRequest


def test_baseline_migration_exists() -> None:
    migration_path = Path("migrations/versions/0001_baseline.py")
    assert migration_path.exists()

    spec = importlib.util.spec_from_file_location("baseline", migration_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0001_baseline"
    assert hasattr(module, "upgrade")
    assert hasattr(module, "downgrade")


def test_response_models_validate_standard_shapes() -> None:
    success = SuccessResponse[dict](data={"id": "demo"})
    paginated = PaginatedResponse[dict](
        data=[{"id": "demo"}],
        page=1,
        page_size=50,
        total=1,
    )

    assert success.success is True
    assert paginated.total == 1
    assert paginated_response([{"id": "demo"}], page=1, page_size=50, total=1) == {
        "success": True,
        "data": [{"id": "demo"}],
        "page": 1,
        "page_size": 50,
        "total": 1,
    }


def test_validation_rejects_oversized_payloads() -> None:
    too_large = "x" * 20_001

    try:
        JobImportTextRequest(raw_text=too_large)
    except ValidationError as exc:
        assert "String should have at most 20000 characters" in str(exc)
    else:
        raise AssertionError("Expected oversized job import text to be rejected")


def test_note_validation_rejects_empty_notes() -> None:
    try:
        ApplicationNoteRequest(note="")
    except ValidationError as exc:
        assert "String should have at least 1 character" in str(exc)
    else:
        raise AssertionError("Expected empty notes to be rejected")


def test_validation_errors_use_standard_error_shape() -> None:
    client = TestClient(app)
    response = client.post("/jobs/import-text", json={"raw_text": ""})

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == "Request validation failed"


def test_applications_router_supports_pagination_filters(monkeypatch) -> None:
    application_id = uuid4()
    candidate_id = uuid4()
    job_id = uuid4()

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_list_applications(
        connection,
        *,
        status=None,
        candidate_id=None,
        job_id=None,
        page=1,
        page_size=50,
    ):
        assert status == "applied"
        assert candidate_id == candidate_id_filter
        assert job_id == job_id_filter
        assert page == 2
        assert page_size == 10
        return (
            [
                {
                    "id": application_id,
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "status": "applied",
                }
            ],
            1,
        )

    candidate_id_filter = candidate_id
    job_id_filter = job_id

    import app.routers.applications as applications_router

    monkeypatch.setattr(
        applications_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(
        applications_router,
        "list_applications",
        fake_list_applications,
    )

    client = TestClient(app)
    response = client.get(
        "/applications",
        params={
            "status": "applied",
            "candidate_id": str(candidate_id),
            "job_id": str(job_id),
            "page": 2,
            "page_size": 10,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"][0]["status"] == "applied"
    assert body["page"] == 2
    assert body["page_size"] == 10
    assert body["total"] == 1
