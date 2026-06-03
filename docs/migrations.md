# Database Migrations

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Strategy

Sprint 9 introduces Alembic as the database migration framework.

The current baseline migration is:

```text
migrations/versions/0001_baseline.py
```

`database/schema.sql` remains as a readable bootstrap schema for local development
and review. Future schema changes should be added as new Alembic revisions first,
then reflected in `database/schema.sql` when the full schema reference changes.

## Configuration

Alembic reads `DATABASE_URL` from the environment when available. If it is not set,
the demo local PostgreSQL URL in `alembic.ini` is used.

Use SQLAlchemy's psycopg v3 dialect in runtime and production examples:

```text
postgresql+psycopg://user:password@postgres:5432/database
```

Do not use the bare `postgresql://` form for production migration runs unless the
image also installs a compatible default PostgreSQL driver. The backend image
ships with `psycopg[binary]`, so the explicit `postgresql+psycopg://` scheme keeps
Alembic, SQLAlchemy, and the application aligned on psycopg v3.

```bash
alembic heads
alembic upgrade head
```

## CI validation

CI validates that Alembic can load the migration tree:

```bash
alembic heads
```

This keeps migration files syntactically valid without requiring a live PostgreSQL
service for every pull request.

## Local migration workflow

1. Update or add repository code and schema changes.
2. Create a new Alembic revision.
3. Add explicit upgrade and downgrade SQL.
4. Run:

```bash
alembic upgrade head
pytest
```

5. Keep changes deterministic and avoid storing private career data in migrations.

## Status events addition

Sprint 9 adds `application_status_events` to track application workflow history while
preserving `applications.status` as the current state.

## Authentication and ownership addition

Sprint 11 adds `0003_auth_ownership.py`.

The migration creates:

- `users`
- `refresh_tokens`
- `auth_audit_events`

It also backfills a demo owner for existing local data and adds `user_id` ownership
columns to private career records. Existing candidate profiles, applications, notes,
outcomes, matches, and briefings are assigned to the demo owner during upgrade so a
clean upgrade path exists for development databases.

Run the full migration chain from an empty database with:

```bash
alembic upgrade head
```
