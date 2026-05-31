# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from psycopg import Connection


def create_user(
    connection: Connection,
    *,
    email: str,
    display_name: str,
    password_hash: str,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (
                email,
                display_name,
                password_hash
            )
            VALUES (%s, %s, %s)
            RETURNING id, email, display_name, created_at, updated_at
            """,
            (email.lower(), display_name, password_hash),
        )
        user = cursor.fetchone()
    create_auth_audit_event(connection, user["id"], "register")
    return user


def get_user_by_email(connection: Connection, email: str) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email.lower(),),
        )
        return cursor.fetchone()


def get_user(connection: Connection, user_id: UUID) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, display_name, created_at, updated_at
            FROM users
            WHERE id = %s
            """,
            (user_id,),
        )
        return cursor.fetchone()


def create_refresh_token_record(
    connection: Connection,
    *,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO refresh_tokens (
                user_id,
                token_hash,
                expires_at
            )
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (user_id, token_hash, expires_at),
        )
        return cursor.fetchone()


def get_refresh_token_record(connection: Connection, token_hash: str) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM refresh_tokens
            WHERE token_hash = %s
              AND revoked_at IS NULL
              AND expires_at > now()
            """,
            (token_hash,),
        )
        return cursor.fetchone()


def create_auth_audit_event(
    connection: Connection,
    user_id: UUID,
    event_type: str,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO auth_audit_events (
                user_id,
                event_type
            )
            VALUES (%s, %s)
            RETURNING *
            """,
            (user_id, event_type),
        )
        return cursor.fetchone()
