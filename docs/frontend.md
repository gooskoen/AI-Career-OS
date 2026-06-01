# Frontend Architecture

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Purpose

Sprint 13 adds the first user-facing private beta experience for AI-Career-OS. The
frontend is an API-driven React application that consumes existing backend endpoints
without duplicating career workflow business logic.

## Stack

- React
- TypeScript
- Vite
- Tailwind CSS
- Vitest and Testing Library

The frontend lives in `frontend/` and is intentionally separate from the FastAPI
backend.

## Routing

Sprint 13 keeps routing lightweight inside the React app state:

- Dashboard
- Applications
- Insights
- Profile

Protected views are only rendered after a successful authentication flow. The app
stores session tokens in browser session storage and retries authenticated requests
once after refreshing the access token.

## API Integration

All backend calls go through `frontend/src/api.ts`.

Authentication:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`

Dashboard and insights:

- `GET /reporting/dashboard`
- `GET /reporting/funnel`
- `GET /reporting/outcomes`
- `GET /reporting/skills`
- `GET /reporting/recommendations`

Applications:

- `GET /applications/board`
- `POST /applications/{id}/transition`
- `GET /applications/{id}/summary`

Profile:

- `GET /candidates`

## Component Hierarchy

```text
App
+-- AuthScreen
+-- Shell
    +-- Navigation
    +-- DashboardPage
    |   +-- Metric
    |   +-- FunnelSummary
    +-- ApplicationsPage
    |   +-- Kanban lanes
    |   +-- ApplicationDetail
    +-- InsightsPage
    |   +-- FunnelSummary
    |   +-- Outcome analytics
    |   +-- Skill analytics
    |   +-- Recommendation analytics
    +-- ProfilePage
```

## Kanban Interaction

The application board renders the existing pipeline statuses:

- drafted
- applied
- recruiter_replied
- interview_scheduled
- interview_completed
- offer_received
- hired
- rejected
- withdrawn

Cards can be dragged between lanes. Dropping a card calls
`POST /applications/{id}/transition`; the board is then reloaded from the backend.

## Beta Workflow

The UI is designed to support the private beta workflow:

Register -> Login -> Create Candidate -> Import Job -> Review Match -> Generate
Package -> Create Application -> Move Through Pipeline -> Record Outcome -> View
Insights.

Sprint 13 includes a guided beta workflow panel that calls the existing APIs for
candidate creation, job import, match review, package generation, application
creation, pipeline movement, and outcome recording. It remains API-first and does not
duplicate backend scoring or workflow rules.

## Guardrails

Sprint 13 does not add:

- recruiter CRM
- AI features
- LLM integration
- automation
- email sending
- LinkedIn automation
- browser automation
- backend redesign
