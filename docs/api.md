# API Notes

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Core endpoints

- `GET /health`
- `GET /demo/candidate`
- `GET /demo/match`
- `POST /match`
- `POST /briefing`
- `POST /applications/package`
- `POST /applications`
- `GET /applications`
- `GET /applications/{application_id}`
- `PATCH /applications/{application_id}/status`
- `GET /applications/{application_id}/status-events`
- `POST /applications/{application_id}/notes`
- `POST /intelligence/company`
- `POST /outcomes`
- `GET /outcomes/{candidate_id}`
- `GET /insights/candidate/{candidate_id}`
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

The API does not implement dashboards, kanban boards, reporting dashboards,
recruiter CRM, authentication, LLM calls, web browsing, LinkedIn automation, or
automatic applications in Sprint 9.
