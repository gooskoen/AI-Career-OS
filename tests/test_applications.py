# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import uuid4

from app.application_domain import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationNextActionRequest,
    ApplicationStatusUpdateRequest,
)
from app.feedback import OutcomeRequest
from app.repositories import (
    create_application,
    create_application_note,
    create_application_outcome,
    application_artifact_readiness,
    application_board,
    application_summary,
    get_application,
    list_application_status_events,
    list_applications,
    update_application_next_action,
    update_application_status,
)


def test_application_creation() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    application_id = uuid4()
    connection = FakeConnection(
        [
            {
                "id": application_id,
                "candidate_id": candidate_id,
                "job_id": job_id,
                "status": "drafted",
                "source": "manual",
            },
        ]
    )

    row = create_application(
        connection,
        ApplicationCreateRequest(
            candidate_id=candidate_id,
            job_id=job_id,
            source="manual",
        ),
    )

    assert row["candidate_id"] == candidate_id
    assert row["job_id"] == job_id
    assert row["status"] == "drafted"
    assert "INSERT INTO applications" in connection.cursor_obj.queries[0]
    assert "INSERT INTO application_status_events" in connection.cursor_obj.queries[1]
    assert connection.cursor_obj.params[1] == (application_id, None, "drafted")


def test_application_retrieval() -> None:
    application_id = uuid4()
    connection = FakeConnection(
        [
            {"id": application_id, "status": "applied"},
            {"total": 1},
            [{"id": application_id, "status": "applied"}],
        ]
    )

    row = get_application(connection, application_id)
    rows, total = list_applications(connection)

    assert row["id"] == application_id
    assert total == 1
    assert rows == [{"id": application_id, "status": "applied"}]
    assert "ORDER BY created_at DESC" in connection.cursor_obj.last_query


def test_status_updates() -> None:
    application_id = uuid4()
    connection = FakeConnection(
        [
            {"status": "applied"},
            {"id": application_id, "status": "interview_scheduled"},
        ]
    )

    row = update_application_status(
        connection,
        application_id,
        ApplicationStatusUpdateRequest(status="interview_scheduled"),
    )

    assert row["status"] == "interview_scheduled"
    assert "UPDATE applications" in connection.cursor_obj.queries[1]
    assert connection.cursor_obj.params[1] == ("interview_scheduled", application_id)
    assert "INSERT INTO application_status_events" in connection.cursor_obj.queries[2]
    assert connection.cursor_obj.params[2] == (
        application_id,
        "applied",
        "interview_scheduled",
    )


def test_status_update_missing_application_returns_none() -> None:
    connection = FakeConnection([None])

    row = update_application_status(
        connection,
        uuid4(),
        ApplicationStatusUpdateRequest(status="interview_scheduled"),
    )

    assert row is None
    assert len(connection.cursor_obj.queries) == 1


def test_application_status_event_history() -> None:
    application_id = uuid4()
    connection = FakeConnection(
        [
            [
                {
                    "application_id": application_id,
                    "previous_status": "drafted",
                    "new_status": "applied",
                }
            ]
        ]
    )

    rows = list_application_status_events(connection, application_id)

    assert rows[0]["new_status"] == "applied"
    assert "application_status_events" in connection.cursor_obj.last_query


def test_application_board_groups_by_pipeline_stage() -> None:
    connection = FakeConnection(
        [
            [
                {"id": uuid4(), "status": "drafted"},
                {"id": uuid4(), "status": "applied"},
                {"id": uuid4(), "status": "applied"},
            ]
        ]
    )

    board = application_board(connection)

    assert list(board.keys()) == [
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
    assert len(board["applied"]) == 2
    assert "LIMIT %s" in connection.cursor_obj.last_query


def test_next_action_updates_application_without_status_event() -> None:
    application_id = uuid4()
    connection = FakeConnection(
        [
            {
                "id": application_id,
                "status": "applied",
                "next_action": "follow up recruiter",
                "next_action_due": "2026-06-07",
            }
        ]
    )

    row = update_application_next_action(
        connection,
        application_id,
        ApplicationNextActionRequest(
            next_action="follow up recruiter",
            due_date="2026-06-07",
        ),
    )

    assert row["next_action"] == "follow up recruiter"
    assert connection.cursor_obj.last_params[2] == application_id
    assert all(
        "INSERT INTO application_status_events" not in query
        for query in connection.cursor_obj.queries
    )


def test_artifact_readiness_reflects_application_references() -> None:
    readiness = application_artifact_readiness(
        {
            "match_result_id": uuid4(),
            "application_package_id": uuid4(),
            "company_intelligence_id": None,
        }
    )

    assert readiness == {
        "match_ready": True,
        "package_ready": True,
        "intelligence_ready": False,
    }


def test_application_summary_combines_application_context() -> None:
    application_id = uuid4()
    connection = FakeConnection(
        [
            {
                "id": application_id,
                "status": "interview_scheduled",
                "next_action": "prepare interview",
                "next_action_due": "2026-06-10",
                "match_result_id": uuid4(),
                "application_package_id": None,
                "company_intelligence_id": uuid4(),
            },
            [{"note": "Prepare STAR story."}],
            {"outcome": "interview_scheduled"},
            [{"new_status": "interview_scheduled"}],
        ]
    )

    summary = application_summary(connection, application_id)

    assert summary is not None
    assert summary["current_status"] == "interview_scheduled"
    assert summary["next_action"] == "prepare interview"
    assert summary["latest_notes"] == [{"note": "Prepare STAR story."}]
    assert summary["latest_outcome"] == {"outcome": "interview_scheduled"}
    assert summary["artifact_readiness"]["match_ready"] is True


def test_outcome_linkage() -> None:
    application_id = uuid4()
    connection = FakeConnection([{"id": uuid4(), "application_id": application_id}])

    row = create_application_outcome(
        connection,
        OutcomeRequest(
            candidate_id=uuid4(),
            job_id=uuid4(),
            application_id=application_id,
            outcome="recruiter_replied",
            notes="Recruiter replied.",
        ),
    )

    assert row["application_id"] == application_id
    assert "application_id" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params[2] == application_id


def test_note_creation_redacts_private_data() -> None:
    application_id = uuid4()
    connection = FakeConnection([{"id": uuid4(), "application_id": application_id}])

    create_application_note(
        connection,
        application_id,
        ApplicationNoteRequest(
            note="Recruiter email alex@example.com and phone +32 499 12 34 56."
        ),
    )

    stored_note = connection.cursor_obj.last_params[1]
    assert "alex@example.com" not in stored_note
    assert "+32 499 12 34 56" not in stored_note
    assert "[redacted]" in stored_note


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
        self.queries = []
        self.params = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params
        self.queries.append(query)
        self.params.append(params)

    def fetchone(self):
        result = self.results.pop(0)
        return result

    def fetchall(self):
        result = self.results.pop(0)
        return result if isinstance(result, list) else [result]
