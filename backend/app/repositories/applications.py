# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from psycopg import Connection

from app.application_domain import (
    ApplicationCreateRequest,
    ApplicationNoteRequest,
    ApplicationNextActionRequest,
    ApplicationStatusUpdateRequest,
    APPLICATION_STATUSES,
    sanitize_note,
)


def create_application(
    connection: Connection,
    application: ApplicationCreateRequest,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO applications (
                candidate_id,
                job_id,
                status,
                source,
                match_result_id,
                application_package_id,
                company_intelligence_id,
                next_action,
                next_action_due
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                application.candidate_id,
                application.job_id,
                application.status,
                application.source,
                application.match_result_id,
                application.application_package_id,
                application.company_intelligence_id,
                None,
                None,
            ),
        )
        created = cursor.fetchone()
        _create_status_event(cursor, created["id"], None, created["status"])
        return created


def get_application(connection: Connection, application_id: UUID) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM applications WHERE id = %s", (application_id,))
        return cursor.fetchone()


def list_applications(
    connection: Connection,
    *,
    status: str | None = None,
    candidate_id: UUID | None = None,
    job_id: UUID | None = None,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[dict], int]:
    where_clauses = []
    params: list[object] = []

    if status is not None:
        where_clauses.append("status = %s")
        params.append(status)
    if candidate_id is not None:
        where_clauses.append("candidate_id = %s")
        params.append(candidate_id)
    if job_id is not None:
        where_clauses.append("job_id = %s")
        params.append(job_id)

    where_sql = ""
    if where_clauses:
        where_sql = "WHERE " + " AND ".join(where_clauses)

    offset = (page - 1) * page_size

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT count(*) AS total FROM applications {where_sql}", params)
        total = cursor.fetchone()["total"]

        cursor.execute(
            f"""
            SELECT *
            FROM applications
            {where_sql}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            [*params, page_size, offset],
        )
        return cursor.fetchall(), total


def application_board(connection: Connection, *, page_size: int = 100) -> dict[str, list[dict]]:
    board = {status: [] for status in APPLICATION_STATUSES}
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM applications
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (page_size,),
        )
        for row in cursor.fetchall():
            if row["status"] in board:
                board[row["status"]].append(row)
    return board


def update_application_status(
    connection: Connection,
    application_id: UUID,
    status_update: ApplicationStatusUpdateRequest,
) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT status FROM applications WHERE id = %s", (application_id,))
        current = cursor.fetchone()
        if current is None:
            return None

        previous_status = current["status"]
        cursor.execute(
            """
            UPDATE applications
            SET status = %s,
                updated_at = now()
            WHERE id = %s
            RETURNING *
            """,
            (status_update.status, application_id),
        )
        updated = cursor.fetchone()
        _create_status_event(
            cursor,
            application_id,
            previous_status,
            status_update.status,
        )
        return updated


def update_application_next_action(
    connection: Connection,
    application_id: UUID,
    next_action: ApplicationNextActionRequest,
) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE applications
            SET next_action = %s,
                next_action_due = %s,
                updated_at = now()
            WHERE id = %s
            RETURNING *
            """,
            (next_action.next_action, next_action.due_date, application_id),
        )
        updated = cursor.fetchone()
        return updated


def application_artifact_readiness(application: dict) -> dict:
    return {
        "match_ready": application.get("match_result_id") is not None,
        "package_ready": application.get("application_package_id") is not None,
        "intelligence_ready": application.get("company_intelligence_id") is not None,
    }


def list_application_status_events(
    connection: Connection,
    application_id: UUID,
) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM application_status_events
            WHERE application_id = %s
            ORDER BY created_at ASC
            """,
            (application_id,),
        )
        return cursor.fetchall()


def create_application_note(
    connection: Connection,
    application_id: UUID,
    note: ApplicationNoteRequest,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO application_notes (
                application_id,
                note
            )
            VALUES (%s, %s)
            RETURNING *
            """,
            (application_id, sanitize_note(note.note)),
        )
        return cursor.fetchone()


def latest_application_notes(
    connection: Connection,
    application_id: UUID,
    *,
    limit: int = 5,
) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM application_notes
            WHERE application_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (application_id, limit),
        )
        return cursor.fetchall()


def latest_application_outcome(
    connection: Connection,
    application_id: UUID,
) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM application_outcomes
            WHERE application_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (application_id,),
        )
        return cursor.fetchone()


def application_summary(connection: Connection, application_id: UUID) -> dict | None:
    application = get_application(connection, application_id)
    if application is None:
        return None

    return {
        "application": application,
        "current_status": application["status"],
        "next_action": application.get("next_action"),
        "next_action_due": application.get("next_action_due"),
        "latest_notes": latest_application_notes(connection, application_id),
        "artifact_readiness": application_artifact_readiness(application),
        "latest_outcome": latest_application_outcome(connection, application_id),
        "status_history": list_application_status_events(connection, application_id),
    }


def _create_status_event(
    cursor,
    application_id: UUID,
    previous_status: str | None,
    new_status: str,
) -> None:
    cursor.execute(
        """
        INSERT INTO application_status_events (
            application_id,
            previous_status,
            new_status
        )
        VALUES (%s, %s, %s)
        """,
        (application_id, previous_status, new_status),
    )
