# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from psycopg import Connection

from app.schemas import JobDescription


def create_job(connection: Connection, job: JobDescription) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO job_descriptions (
                title,
                company,
                location,
                description,
                required_skills,
                nice_to_have_skills,
                source,
                source_url,
                external_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                job.title,
                job.company,
                job.location,
                job.description,
                job.required_skills,
                job.nice_to_have_skills,
                job.source,
                job.source_url,
                job.external_id,
            ),
        )
        return cursor.fetchone()


def find_duplicate_job(connection: Connection, job: JobDescription) -> dict | None:
    with connection.cursor() as cursor:
        if job.source_url:
            cursor.execute(
                """
                SELECT *
                FROM job_descriptions
                WHERE source_url = %s
                ORDER BY imported_at DESC, created_at DESC
                LIMIT 1
                """,
                (job.source_url,),
            )
            duplicate = cursor.fetchone()
            if duplicate:
                return duplicate

        cursor.execute(
            """
            SELECT *
            FROM job_descriptions
            WHERE lower(company) = lower(%s)
              AND lower(title) = lower(%s)
              AND COALESCE(lower(location), '') = COALESCE(lower(%s), '')
            ORDER BY imported_at DESC, created_at DESC
            LIMIT 1
            """,
            (job.company, job.title, job.location),
        )
        return cursor.fetchone()


def create_or_get_imported_job(
    connection: Connection,
    job: JobDescription,
) -> tuple[dict, bool]:
    duplicate = find_duplicate_job(connection, job)
    if duplicate:
        return duplicate, True
    return create_job(connection, job), False


def list_jobs(connection: Connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC")
        return cursor.fetchall()


def get_job(connection: Connection, job_id: UUID) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM job_descriptions WHERE id = %s", (job_id,))
        return cursor.fetchone()


def job_from_row(row: dict) -> JobDescription:
    return JobDescription(
        title=row["title"],
        company=row["company"],
        location=row["location"],
        description=row["description"],
        required_skills=row["required_skills"],
        nice_to_have_skills=row["nice_to_have_skills"],
        source=row["source"],
        source_url=row["source_url"],
        external_id=row["external_id"],
    )
