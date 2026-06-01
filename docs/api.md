# API Notes

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Core endpoints

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /demo/candidate`
- `GET /demo/match`
- `POST /match`
- `POST /briefing`
- `POST /applications/package`
- `POST /applications`
- `GET /applications`
- `GET /applications/board`
- `GET /applications/{application_id}`
- `PATCH /applications/{application_id}/status`
- `POST /applications/{application_id}/transition`
- `PATCH /applications/{application_id}/next-action`
- `GET /applications/{application_id}/readiness`
- `GET /applications/{application_id}/summary`
- `GET /applications/{application_id}/status-events`
- `POST /applications/{application_id}/notes`
- `POST /intelligence/company`
- `POST /outcomes`
- `GET /outcomes/{candidate_id}`
- `GET /insights/candidate/{candidate_id}`
- `GET /reporting/dashboard`
- `GET /reporting/funnel`
- `GET /reporting/applications`
- `GET /reporting/outcomes`
- `GET /reporting/skills`
- `GET /reporting/recommendations`
- `POST /candidates`
- `GET /candidates`
- `POST /jobs`
- `GET /jobs`
- `POST /jobs/import-text`
- `POST /jobs/import-url`
- `POST /matches/persist`
- `GET /matches`
- `POST /briefings/persist`
- `GET /briefings`

## Authentication

Sprint 11 introduces simple JWT authentication. Register or log in to receive an
access token, then pass it as a bearer token to protected endpoints.

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "display_name": "Demo User",
    "password": "use-a-long-demo-password"
  }'
```

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "use-a-long-demo-password"
  }'
```

Protected requests use:

```bash
curl http://localhost:8000/applications \
  -H "Authorization: Bearer <access-token>"
```

Refresh tokens can be exchanged for a new access token:

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh-token>"}'
```

Candidate profiles, applications, notes, outcomes, persisted matches, and persisted
briefings are scoped to the authenticated user.

## Reporting

Sprint 12 adds read-only, user-scoped reporting endpoints. All reporting endpoints
require the same bearer token as other private workflow endpoints.

Supported `time_window` values:

- `last_30_days`
- `last_90_days`
- `last_year`
- `all_time`

Example:

```bash
curl "http://localhost:8000/reporting/dashboard?time_window=last_90_days" \
  -H "Authorization: Bearer <access-token>"
```

Reporting endpoints are deterministic and do not call LLMs, browse the web, send
email, or perform automation.

## Application filtering and pagination

`GET /applications` supports:

- `status`
- `candidate_id`
- `job_id`
- `page`
- `page_size`

Example:

```bash
curl "http://localhost:8000/applications?status=applied&page=1&page_size=25"
```

Response shape:

```json
{
  "success": true,
  "data": [],
  "page": 1,
  "page_size": 25,
  "total": 0
}
```

## Status history

Application status updates preserve the current `applications.status` field and add a
history record to `application_status_events`.

```bash
curl http://localhost:8000/applications/<application-id>/status-events
```

## Application board

`GET /applications/board` returns applications grouped by pipeline stage:

```bash
curl "http://localhost:8000/applications/board?page_size=100"
```

```json
{
  "drafted": [],
  "applied": [],
  "recruiter_replied": [],
  "interview_scheduled": [],
  "interview_completed": [],
  "offer_received": [],
  "hired": [],
  "rejected": [],
  "withdrawn": []
}
```

## Pipeline transitions

```bash
curl -X POST http://localhost:8000/applications/<application-id>/transition \
  -H "Content-Type: application/json" \
  -d '{"status": "interview_scheduled"}'
```

Transitions update the current application status and write status history. Outcomes
remain separate business results.

## Next action and follow-up

```bash
curl -X PATCH http://localhost:8000/applications/<application-id>/next-action \
  -H "Content-Type: application/json" \
  -d '{"next_action": "prepare interview", "due_date": "2026-06-10"}'
```

## Artifact readiness

```bash
curl http://localhost:8000/applications/<application-id>/readiness
```

```json
{
  "match_ready": true,
  "package_ready": true,
  "intelligence_ready": false
}
```

## Application summary

```bash
curl http://localhost:8000/applications/<application-id>/summary
```

The summary includes the application, current status, next action, latest notes,
artifact readiness, latest outcome, and status history.

## Validation errors

Validation errors return a standard error response:

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": []
  }
}
```

## Guardrails

The API does not implement recruiter CRM, OAuth/social login, LLM calls, web browsing,
LinkedIn automation, automatic applications, email sending, or a dashboard frontend.
