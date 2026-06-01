# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from psycopg import Connection

from app.feedback import OutcomeRequest, sanitize_notes


def create_application_outcome(
    connection: Connection,
    outcome: OutcomeRequest,
    user_id: UUID,
) -> dict:
    _require_user_id(user_id)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO application_outcomes (
                user_id,
                candidate_id,
                job_id,
                application_id,
                outcome,
                notes,
                cv_edits_applied,
                cover_letter_used,
                interview_prep_used,
                skills,
                job_family
            )
            SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            WHERE EXISTS (
                SELECT 1
                FROM applications
                WHERE id = %s
                  AND user_id = %s
                  AND candidate_id = %s
                  AND job_id = %s
            )
            RETURNING *
            """,
            (
                user_id,
                outcome.candidate_id,
                outcome.job_id,
                outcome.application_id,
                outcome.outcome,
                sanitize_notes(outcome.notes),
                outcome.cv_edits_applied,
                outcome.cover_letter_used,
                outcome.interview_prep_used,
                outcome.skills,
                outcome.job_family,
                outcome.application_id,
                user_id,
                outcome.candidate_id,
                outcome.job_id,
            ),
        )
        return cursor.fetchone()


def list_application_outcomes(
    connection: Connection,
    candidate_id: UUID,
    user_id: UUID,
) -> list[dict]:
    _require_user_id(user_id)
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM application_outcomes
            WHERE candidate_id = %s
              AND user_id = %s
            ORDER BY created_at ASC
            """,
            (candidate_id, user_id),
        )
        return cursor.fetchall()


def _require_user_id(user_id: UUID) -> None:
    if user_id is None:
        raise ValueError("user_id is required for outcome repository access")
