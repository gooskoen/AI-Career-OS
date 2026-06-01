# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.dependencies import current_user
from app.main import app
from app.reporting import (
    application_report,
    candidate_insights_v2,
    cutoff_for_time_window,
    dashboard_report,
    funnel_report,
    outcome_report,
    recommendation_report,
    skill_report,
)
from app.repositories import list_reporting_applications, list_reporting_outcomes


def test_dashboard_calculations() -> None:
    applications = [
        _application("drafted"),
        _application("applied"),
        _application("interview_scheduled"),
        _application("offer_received"),
        _application("hired"),
        _application("rejected"),
    ]

    report = dashboard_report(applications)

    assert report["active_applications"] == 4
    assert report["interviews_scheduled"] == 1
    assert report["offers_received"] == 1
    assert report["hires"] == 1
    assert report["rejections"] == 1
    assert report["pipeline_totals"]["withdrawn"] == 0


def test_funnel_calculations_use_outcome_history() -> None:
    application_id = uuid4()
    applications = [
        _application("rejected", application_id=application_id),
        _application("applied"),
    ]
    outcomes = [
        _outcome(application_id, "recruiter_replied"),
        _outcome(application_id, "interview_scheduled"),
        _outcome(application_id, "offer_received"),
    ]

    report = funnel_report(applications, outcomes)

    assert report["applications"] == 2
    assert report["recruiter_replies"] == 1
    assert report["interviews"] == 1
    assert report["offers"] == 1
    assert report["application_to_reply_rate"] == 0.5


def test_application_analytics() -> None:
    applications = [
        _application(
            "applied",
            source="manual",
            job_title="Data Analyst",
            created_at=datetime(2026, 6, 1, tzinfo=UTC),
        ),
        _application(
            "hired",
            source="linkedin",
            job_title="Backend Engineer",
            created_at=datetime(2026, 6, 2, tzinfo=UTC),
        ),
    ]
    outcomes = [
        _outcome(applications[1]["id"], "hired", job_family="Engineering"),
    ]

    report = application_report(applications, outcomes)

    assert report["applications_by_status"]["applied"] == 1
    assert report["applications_by_source"]["linkedin"] == 1
    assert report["applications_by_month"]["2026-06"] == 2
    assert report["applications_by_job_family"]["Engineering"] == 1
    assert report["applications_by_job_family"]["Data"] == 1


def test_outcome_analytics() -> None:
    applications = [_application("applied"), _application("rejected")]
    outcomes = [
        _outcome(applications[0]["id"], "offer_received"),
        _outcome(applications[1]["id"], "rejected"),
    ]

    report = outcome_report(applications, outcomes)

    assert report["rejection_rate"] == 0.5
    assert report["offer_rate"] == 0.5
    assert report["hire_rate"] == 0.0
    assert report["outcome_trends"]["unknown"]["offer_received"] == 1


def test_skill_analytics() -> None:
    outcomes = [
        _outcome(uuid4(), "offer_received", skills=["Python", "SQL"]),
        _outcome(uuid4(), "recruiter_replied", skills=["Python"]),
        _outcome(uuid4(), "rejected", skills=["BPMN"]),
    ]

    report = skill_report(outcomes)

    assert report["strongest_performing_skills"][0] == "Python"
    assert report["most_successful_skills"] == ["Python", "SQL"]
    assert report["weakest_performing_skills"] == ["BPMN"]
    assert report["rejection_linked_skills"] == ["BPMN"]


def test_recommendation_analytics() -> None:
    outcomes = [
        _outcome(uuid4(), "applied", cv_edits_applied=True),
        _outcome(uuid4(), "rejected", cover_letter_used=True),
    ]

    report = recommendation_report(outcomes)

    assert report["recommendations_followed"]["cv_edits_applied"] == 1
    assert report["recommendations_ignored"]["interview_prep_used"] == 2
    assert report["recommendation_usage_rates"]["cover_letter_used"] == 0.5


def test_candidate_insights_v2_adds_reporting_fields() -> None:
    outcomes = [
        _outcome(
            uuid4(),
            "offer_received",
            skills=["Python", "SQL"],
            job_family="AI Operations",
        ),
        _outcome(
            uuid4(),
            "rejected",
            notes="Rejected for seniority and skill gap.",
            skills=["BPMN"],
        ),
    ]

    insights = candidate_insights_v2(outcomes)

    assert insights["top_job_families"] == ["AI Operations"]
    assert "seniority mismatch" in insights["recurring_rejection_patterns"]
    assert insights["strongest_skill_clusters"]
    assert insights["focus_recommendations"]


def test_time_window_filtering_cutoffs() -> None:
    now = datetime.now(UTC)

    assert cutoff_for_time_window("all_time") is None
    assert now - cutoff_for_time_window("last_30_days") < timedelta(days=31)
    assert now - cutoff_for_time_window("last_90_days") < timedelta(days=91)
    assert now - cutoff_for_time_window("last_year") < timedelta(days=366)


def test_reporting_repositories_are_user_scoped() -> None:
    user_id = uuid4()
    since = datetime(2026, 6, 1, tzinfo=UTC)
    connection = FakeConnection([[{"id": uuid4()}], [{"id": uuid4()}]])

    list_reporting_applications(connection, user_id=user_id, since=since)
    list_reporting_outcomes(connection, user_id=user_id, since=since)

    assert "a.user_id = %s" in connection.cursor_obj.queries[0]
    assert "user_id = %s" in connection.cursor_obj.queries[1]
    assert connection.cursor_obj.params[0][0] == user_id
    assert connection.cursor_obj.params[1][0] == user_id
    assert connection.cursor_obj.params[0][1] == since


def test_reporting_repositories_reject_missing_user_id() -> None:
    connection = FakeConnection([])

    with pytest.raises(ValueError):
        list_reporting_applications(connection, user_id=None)

    with pytest.raises(ValueError):
        list_reporting_outcomes(connection, user_id=None)


def test_reporting_endpoint_enforces_ownership_context(monkeypatch) -> None:
    user_id = uuid4()
    app.dependency_overrides[current_user] = lambda: {
        "id": user_id,
        "email": "demo@example.com",
    }

    def fake_run_database_operation(operation):
        return operation(object())

    def fake_applications(connection, *, user_id=None, since=None):
        assert user_id is not None
        return [_application("applied")]

    def fake_outcomes(connection, *, user_id=None, since=None):
        assert user_id is not None
        return []

    import app.routers.reporting as reporting_router

    monkeypatch.setattr(
        reporting_router,
        "run_database_operation",
        fake_run_database_operation,
    )
    monkeypatch.setattr(
        reporting_router,
        "list_reporting_applications",
        fake_applications,
    )
    monkeypatch.setattr(reporting_router, "list_reporting_outcomes", fake_outcomes)

    response = TestClient(app).get("/reporting/dashboard?time_window=all_time")
    app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["active_applications"] == 1


def _application(
    status: str,
    *,
    application_id=None,
    source: str | None = "manual",
    job_title: str = "AI Operations Engineer",
    created_at=None,
) -> dict:
    return {
        "id": application_id or uuid4(),
        "status": status,
        "source": source,
        "job_source": source,
        "job_title": job_title,
        "created_at": created_at,
    }


def _outcome(
    application_id,
    outcome: str,
    *,
    notes: str = "",
    skills: list[str] | None = None,
    job_family: str | None = None,
    cv_edits_applied: bool = False,
    cover_letter_used: bool = False,
    interview_prep_used: bool = False,
) -> dict:
    return {
        "id": uuid4(),
        "candidate_id": uuid4(),
        "job_id": uuid4(),
        "application_id": application_id,
        "outcome": outcome,
        "notes": notes,
        "skills": skills or [],
        "job_family": job_family,
        "cv_edits_applied": cv_edits_applied,
        "cover_letter_used": cover_letter_used,
        "interview_prep_used": interview_prep_used,
        "created_at": None,
    }


class FakeConnection:
    def __init__(self, results):
        self.cursor_obj = FakeCursor(results)

    def cursor(self):
        return self.cursor_obj


class FakeCursor:
    def __init__(self, results):
        self.results = list(results)
        self.queries = []
        self.params = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params=None):
        self.queries.append(query)
        self.params.append(params)

    def fetchall(self):
        return self.results.pop(0)
