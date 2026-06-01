# Architecture

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Current architecture

AI-Career-OS is a FastAPI and PostgreSQL MVP organized around the `Application`
domain entity. Sprint 11 adds a first-party `User` owner so career data is scoped
to the authenticated account that created it.

```text
User
    |
    v
Candidate
    |
    v
Application current_status
    |
    v
Job

Application
+-- MatchResult
+-- ApplicationPackage
+-- CompanyIntelligence
+-- ApplicationStatusEvent history
+-- ApplicationOutcome business_result
+-- Notes
```

## Backend layout

```text
backend/app/
+-- main.py                 # FastAPI app wiring and router registration
+-- routers/                # HTTP route groups
|   +-- candidates.py
|   +-- jobs.py
|   +-- applications.py
|   +-- matching.py
|   +-- intelligence.py
|   +-- outcomes.py
|   +-- auth.py
+-- repositories/           # PostgreSQL data access by aggregate
|   +-- users.py
|   +-- candidates.py
|   +-- jobs.py
|   +-- applications.py
|   +-- matching.py
|   +-- intelligence.py
|   +-- outcomes.py
+-- application_domain.py   # Application request models and note sanitizing
+-- application_package.py  # Deterministic application package generation
+-- auth.py                 # Password hashing and JWT helpers
+-- briefing.py             # Interview briefing generation
+-- company_intelligence.py # Deterministic company/recruiter preparation
+-- database.py             # PostgreSQL connection helper
+-- dependencies.py         # Shared API helpers
+-- errors.py               # Standard error response handling
+-- feedback.py             # Outcome analytics and insights
+-- ingestion.py            # Manual job import helpers
+-- matching.py             # Deterministic matching and gap analysis
+-- responses.py            # Standard response models
+-- schemas.py              # Shared Pydantic request models
```

## Design principles

- Keep deterministic behavior first.
- Keep Application as the central business object.
- Scope private career data by authenticated user.
- Keep API routes thin and domain-oriented.
- Keep repository functions explicit and readable.
- Avoid LLMs, paid APIs, scraping, LinkedIn automation, and automatic applications.
- Treat notes and candidate data as sensitive.

## Application state model

Sprint 9 separates status, history, and business outcomes:

- `applications.status`: current workflow status.
- `application_status_events`: status transition history.
- `application_outcomes`: real-world business results and recommendation usage.

This keeps the current status fast to read while preserving an audit-friendly timeline.

## Ownership model

Sprint 11 introduces:

- `users`: local user accounts with unique email addresses and hashed passwords.
- `refresh_tokens`: stored refresh token hashes for token renewal.
- `auth_audit_events`: register, login, and refresh audit records.
- `user_id` ownership on candidate profiles, applications, notes, outcomes,
  persisted matches, persisted briefings, and generated artifact tables.

Repository methods that read or write private career data accept `user_id` and scope
queries accordingly. Cross-user reads intentionally return not found responses rather
than revealing that another user's record exists.

## Error model

API errors use a consistent JSON shape:

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

Supported error categories include validation, not found, conflict, service
unavailable, and internal errors.

## Response model direction

Sprint 9 introduces shared response models:

- `SuccessResponse`
- `ErrorResponse`
- `PaginatedResponse`

New list-style endpoints should prefer `PaginatedResponse`. Existing endpoints keep
their domain payloads unless a sprint explicitly migrates them to envelopes.
