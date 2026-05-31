# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from psycopg import Connection

from app.matching import MatchResult


def create_match_result(
    connection: Connection,
    candidate_id: UUID,
    job_id: UUID,
    match: MatchResult,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO match_results (
                candidate_profile_id,
                job_description_id,
                score,
                matched_keywords,
                missing_keywords,
                recommendation
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                candidate_id,
                job_id,
                match.score,
                match.matched_keywords,
                match.missing_keywords,
                match.recommendation,
            ),
        )
        return cursor.fetchone()


def list_match_results(connection: Connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM match_results ORDER BY created_at DESC")
        return cursor.fetchall()


def get_match_result(connection: Connection, match_result_id: UUID) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM match_results WHERE id = %s", (match_result_id,))
        return cursor.fetchone()


def create_interview_briefing(
    connection: Connection,
    match_result_id: UUID,
    briefing: dict,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO interview_briefings (
                match_result_id,
                positioning_statement,
                strengths_to_emphasize,
                gaps_to_prepare,
                likely_interview_topics,
                questions_to_ask
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                match_result_id,
                briefing["positioning_statement"],
                briefing["strengths_to_emphasize"],
                briefing["gaps_to_prepare"],
                briefing["likely_interview_topics"],
                briefing["questions_to_ask"],
            ),
        )
        return cursor.fetchone()


def list_interview_briefings(connection: Connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM interview_briefings ORDER BY created_at DESC")
        return cursor.fetchall()


def match_from_row(row: dict) -> MatchResult:
    return MatchResult(
        score=row["score"],
        matched_keywords=row["matched_keywords"],
        missing_keywords=row["missing_keywords"],
        candidate_highlights=[],
        recommendation=row["recommendation"],
    )
