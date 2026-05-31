# Application Pipeline

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Purpose

Sprint 10 turns the Application aggregate into a workflow-centric pipeline for daily
career management. The implementation is API-first and Kanban-ready, but it does not
add a dashboard frontend.

## Pipeline stages

Applications use the existing status model as pipeline stages:

```text
drafted
applied
recruiter_replied
interview_scheduled
interview_completed
offer_received
hired
rejected
withdrawn
```

`applications.status` remains the current state. `application_status_events` remains
the status history. `application_outcomes` remains the business result history.

## Kanban board endpoint

```bash
curl "http://localhost:8000/applications/board?page_size=100"
```

Response shape:

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

The board output is deterministic and grouped by pipeline stage.

## Status transitions

Use the transition endpoint when moving an application through the pipeline:

```bash
curl -X POST http://localhost:8000/applications/<application-id>/transition \
  -H "Content-Type: application/json" \
  -d '{"status": "interview_scheduled"}'
```

The endpoint updates `applications.status` and writes an `application_status_events`
record. Outcomes are not replaced by transitions.

## Next action and follow-up date

```bash
curl -X PATCH http://localhost:8000/applications/<application-id>/next-action \
  -H "Content-Type: application/json" \
  -d '{
    "next_action": "prepare interview",
    "due_date": "2026-06-10"
  }'
```

Use this for daily work tracking, such as:

- follow up recruiter;
- prepare interview;
- send requested documents;
- review offer.

## Artifact readiness

```bash
curl http://localhost:8000/applications/<application-id>/readiness
```

Response shape:

```json
{
  "match_ready": true,
  "package_ready": true,
  "intelligence_ready": false
}
```

Readiness is derived from Application references:

- `match_result_id`;
- `application_package_id`;
- `company_intelligence_id`.

## Application summary

```bash
curl http://localhost:8000/applications/<application-id>/summary
```

The summary returns:

- application;
- current status;
- next action;
- latest notes;
- artifact readiness;
- latest outcome;
- status history.

## Guardrails

Sprint 10 does not add:

- reporting;
- recruiter CRM;
- authentication;
- AI features;
- LLM integration;
- email sending;
- automation;
- dashboard frontend.
