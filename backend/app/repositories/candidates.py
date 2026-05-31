# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from psycopg import Connection

from app.schemas import CandidateProfile


def create_candidate(
    connection: Connection,
    candidate: CandidateProfile,
    user_id: UUID,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO candidate_profiles (
                user_id,
                display_name,
                headline,
                location,
                summary,
                target_roles,
                skills,
                experience_highlights,
                portfolio_links
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                user_id,
                candidate.name,
                candidate.headline,
                candidate.location,
                candidate.summary,
                candidate.target_roles,
                candidate.skills,
                candidate.experience_highlights,
                candidate.portfolio_links,
            ),
        )
        return cursor.fetchone()


def list_candidates(connection: Connection, user_id: UUID) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM candidate_profiles
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()


def get_candidate(
    connection: Connection,
    candidate_id: UUID,
    user_id: UUID | None = None,
) -> dict | None:
    with connection.cursor() as cursor:
        if user_id is None:
            cursor.execute(
                "SELECT * FROM candidate_profiles WHERE id = %s",
                (candidate_id,),
            )
        else:
            cursor.execute(
                """
                SELECT *
                FROM candidate_profiles
                WHERE id = %s
                  AND user_id = %s
                """,
                (candidate_id, user_id),
            )
        return cursor.fetchone()


def candidate_from_row(row: dict) -> CandidateProfile:
    return CandidateProfile(
        name=row["display_name"],
        headline=row["headline"],
        location=row["location"] or "",
        summary=row["summary"],
        target_roles=row["target_roles"],
        skills=row["skills"],
        experience_highlights=row["experience_highlights"],
        portfolio_links=row["portfolio_links"],
    )
