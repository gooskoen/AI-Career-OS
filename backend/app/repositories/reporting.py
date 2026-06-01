# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from psycopg import Connection


def list_reporting_applications(
    connection: Connection,
    *,
    user_id: UUID,
    since: datetime | None = None,
) -> list[dict]:
    _require_user_id(user_id)
    where_clauses = ["a.user_id = %s"]
    params: list[object] = [user_id]
    if since is not None:
        where_clauses.append("a.created_at >= %s")
        params.append(since)

    where_sql = " AND ".join(where_clauses)

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT
                a.*,
                j.title AS job_title,
                j.company AS job_company,
                j.source AS job_source
            FROM applications a
            JOIN job_descriptions j ON j.id = a.job_id
            WHERE {where_sql}
            ORDER BY a.created_at DESC
            """,
            params,
        )
        return cursor.fetchall()


def list_reporting_outcomes(
    connection: Connection,
    *,
    user_id: UUID,
    since: datetime | None = None,
) -> list[dict]:
    _require_user_id(user_id)
    where_clauses = ["user_id = %s"]
    params: list[object] = [user_id]
    if since is not None:
        where_clauses.append("created_at >= %s")
        params.append(since)

    where_sql = " AND ".join(where_clauses)

    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT *
            FROM application_outcomes
            WHERE {where_sql}
            ORDER BY created_at ASC
            """,
            params,
        )
        return cursor.fetchall()


def _require_user_id(user_id: UUID) -> None:
    if user_id is None:
        raise ValueError("user_id is required for reporting repository access")
