# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import uuid4

from app.application_domain import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationStatusUpdateRequest,
)
from app.feedback import OutcomeRequest
from app.repositories import (
    create_application,
    create_application_note,
    create_application_outcome,
    get_application,
    list_applications,
    update_application_status,
)


def test_application_creation() -> None:
    candidate_id = uuid4()
    job_id = uuid4()
    connection = FakeConnection(
        {
            "id": uuid4(),
            "candidate_id": candidate_id,
            "job_id": job_id,
            "status": "drafted",
            "source": "manual",
        }
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
    assert "INSERT INTO applications" in connection.cursor_obj.last_query


def test_application_retrieval() -> None:
    application_id = uuid4()
    connection = FakeConnection({"id": application_id, "status": "applied"})

    row = get_application(connection, application_id)
    rows = list_applications(connection)

    assert row["id"] == application_id
    assert rows == [{"id": application_id, "status": "applied"}]
    assert "ORDER BY created_at DESC" in connection.cursor_obj.last_query


def test_status_updates() -> None:
    application_id = uuid4()
    connection = FakeConnection({"id": application_id, "status": "interview_scheduled"})

    row = update_application_status(
        connection,
        application_id,
        ApplicationStatusUpdateRequest(status="interview_scheduled"),
    )

    assert row["status"] == "interview_scheduled"
    assert "UPDATE applications" in connection.cursor_obj.last_query
    assert connection.cursor_obj.last_params == ("interview_scheduled", application_id)


def test_outcome_linkage() -> None:
    application_id = uuid4()
    connection = FakeConnection({"id": uuid4(), "application_id": application_id})

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
    connection = FakeConnection({"id": uuid4(), "application_id": application_id})

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
    def __init__(self, result):
        self.cursor_obj = FakeCursor(result)

    def cursor(self):
        return self.cursor_obj


class FakeCursor:
    def __init__(self, result):
        self.result = result
        self.last_query = ""
        self.last_params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params

    def fetchone(self):
        return self.result

    def fetchall(self):
        return [self.result]
