# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    return database_url


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    """Open a short-lived PostgreSQL connection for simple MVP requests."""

    with psycopg.connect(get_database_url(), row_factory=dict_row) as connection:
        yield connection
