# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient

from app.dependencies import current_user
from app.main import app


def _client() -> TestClient:
    app.dependency_overrides[current_user] = lambda: {
        "id": uuid4(),
        "email": "demo@example.com",
    }
    return TestClient(app)


def test_board_endpoint_returns_pipeline_stages(monkeypatch) -> None:
    def fake_run_database_operation(operation):
        return operation(object())

    def fake_board(connection, *, page_size=100, user_id=None):
        assert page_size == 25
        assert user_id is not None
        return {
            "drafted": [{"id": str(uuid4()), "status": "drafted"}],
            "applied": [],
            "recruiter_replied": [],
            "interview_scheduled": [],
            "interview_completed": [],
            "offer_received": [],
            "hired": [],
            "rejected": [],
            "withdrawn": [],
        }

    import app.routers.applications as applications_router

    monkeypatch.setattr(
        applications_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(applications_router, "application_board", fake_board)

    response = _client().get("/applications/board?page_size=25")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert list(response.json().keys()) == [
        "drafted",
        "applied",
        "recruiter_replied",
        "interview_scheduled",
        "interview_completed",
        "offer_received",
        "hired",
        "rejected",
        "withdrawn",
    ]


def test_transition_endpoint_updates_status(monkeypatch) -> None:
    application_id = uuid4()

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_update_status(connection, target_application_id, status_update, user_id=None):
        assert target_application_id == application_id
        assert user_id is not None
        assert status_update.status == "interview_scheduled"
        return {"id": application_id, "status": status_update.status}

    import app.routers.applications as applications_router

    monkeypatch.setattr(
        applications_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(
        applications_router,
        "update_application_status",
        fake_update_status,
    )

    response = _client().post(
        f"/applications/{application_id}/transition",
        json={"status": "interview_scheduled"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "interview_scheduled"


def test_next_action_endpoint_updates_follow_up_date(monkeypatch) -> None:
    application_id = uuid4()

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_update_next_action(connection, target_application_id, next_action, user_id):
        assert target_application_id == application_id
        assert user_id is not None
        assert next_action.next_action == "prepare interview"
        assert str(next_action.due_date) == "2026-06-10"
        return {
            "id": application_id,
            "next_action": next_action.next_action,
            "next_action_due": next_action.due_date,
        }

    import app.routers.applications as applications_router

    monkeypatch.setattr(
        applications_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(
        applications_router,
        "update_application_next_action",
        fake_update_next_action,
    )

    response = _client().patch(
        f"/applications/{application_id}/next-action",
        json={"next_action": "prepare interview", "due_date": "2026-06-10"},
    )
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["next_action"] == "prepare interview"
    assert response.json()["next_action_due"] == "2026-06-10"


def test_readiness_endpoint_reports_artifacts(monkeypatch) -> None:
    application_id = uuid4()

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_get_application(connection, target_application_id, user_id):
        assert target_application_id == application_id
        assert user_id is not None
        return {
            "id": application_id,
            "match_result_id": uuid4(),
            "application_package_id": None,
            "company_intelligence_id": uuid4(),
        }

    import app.routers.applications as applications_router

    monkeypatch.setattr(
        applications_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(applications_router, "get_application", fake_get_application)

    response = _client().get(f"/applications/{application_id}/readiness")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "match_ready": True,
        "package_ready": False,
        "intelligence_ready": True,
    }


def test_summary_endpoint_returns_application_overview(monkeypatch) -> None:
    application_id = uuid4()

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_summary(connection, target_application_id, user_id):
        assert target_application_id == application_id
        assert user_id is not None
        return {
            "application": {"id": application_id, "status": "applied"},
            "current_status": "applied",
            "next_action": "follow up recruiter",
            "latest_notes": [],
            "artifact_readiness": {
                "match_ready": True,
                "package_ready": True,
                "intelligence_ready": False,
            },
            "latest_outcome": None,
            "status_history": [{"new_status": "applied"}],
        }

    import app.routers.applications as applications_router

    monkeypatch.setattr(
        applications_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(applications_router, "application_summary", fake_summary)

    response = _client().get(f"/applications/{application_id}/summary")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["current_status"] == "applied"
    assert response.json()["next_action"] == "follow up recruiter"
    assert response.json()["artifact_readiness"]["match_ready"] is True
