# Authentication

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Overview

Sprint 11 introduces local username/password authentication with JWT access tokens
and refresh tokens. This is a foundation for private beta ownership, not a full
identity platform.

The API does not use OAuth, social login, external identity providers, or email-based
account verification yet.

## Register

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "display_name": "Demo User",
    "password": "use-a-long-demo-password"
  }'
```

Response:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<refresh-token>",
  "token_type": "bearer",
  "user": {
    "id": "<user-id>",
    "email": "demo@example.com",
    "display_name": "Demo User"
  }
}
```

## Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "use-a-long-demo-password"
  }'
```

## Refresh

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh-token>"}'
```

## Authenticated Requests

```bash
curl http://localhost:8000/applications \
  -H "Authorization: Bearer <access-token>"
```

Protected endpoints return `401` when the bearer token is missing, invalid, or
expired.

## Token Design

- Access tokens are signed JWTs using `HS256`.
- Refresh tokens are random opaque tokens.
- Only refresh token hashes are stored in PostgreSQL.
- Set `AUTH_SECRET` in non-demo environments.

## Ownership Rules

Authenticated users can access only their own:

- candidate profiles
- applications
- application notes
- application outcomes
- persisted match results
- persisted interview briefings
- generated artifact records

Cross-user reads return not found responses so the API does not disclose whether
another user's private record exists.
