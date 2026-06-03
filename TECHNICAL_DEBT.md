# Technical Debt Assessment after v0.8.0

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Executive summary

The current technical debt is normal for a sprint-built MVP. Most debt comes from successful growth: the API, schema, and repository layer now support enough domain behavior that they need clearer boundaries before the next product expansion.

The highest leverage debt reduction is to harden the architecture around Application, persistence, API contracts, and tests.

## Quick wins

These items are small and reduce friction quickly:

- Add explicit response models for existing endpoints.
- Add a standard error response model.
- Add pagination parameters to list endpoints.
- Add max length constraints to request models with free-text fields.
- Move route groups out of `main.py` into routers.
- Split repository functions by aggregate.
- Add README links to dedicated docs once docs are split.
- Add tests for error response shape.
- Add tests for oversized text inputs.
- Add more redaction test cases.

## Medium priority items

These items should be planned into one or two focused hardening sprints:

- Add database migrations.
- Add live PostgreSQL integration tests in CI or an optional local test profile.
- Add `application_packages` persistence.
- Add `company_intelligence_reports` persistence.
- Add `application_status_events` for status history.
- Clarify source values with a controlled enum or reference table.
- Normalize company data if recruiter or reporting features are next.
- Add API versioning under `/v1`.
- Add consistent response envelopes for created, list, and error responses.
- Add filters for applications by status, source, candidate, job, and date.
- Add contract tests for core endpoints.

## Major refactors

These should wait until there is agreement on v1 architecture:

- Introduce a service layer between API routes and repository functions.
- Introduce auth, user/workspace ownership, and authorization checks.
- Introduce a formal document/artifact model for generated outputs.
- Introduce a reporting read model for dashboard performance.
- Introduce event-style tracking for application status, outcomes, recommendation usage, and package generation.
- Split candidate profile data into structured sub-entities if reporting requires it.

## Architectural risks

### Application status and outcomes can diverge

Application status represents current state. Outcomes represent timeline events. Both are valuable, but the relationship should be explicit.

Risk:

- A direct status update may not create an outcome event.
- An outcome event may update status in a way that obscures previous transitions.

Recommended fix:

- Add `application_status_events`.
- Treat `applications.status` as current state.
- Treat outcomes as result events linked to applications.

### Generated artifacts are not fully persisted

Application package and company intelligence outputs are important domain artifacts. Application currently has reference fields for them, but the underlying data is not yet modeled as first-class tables.

Risk:

- Users cannot reliably retrieve what was generated for an application.
- Future dashboards cannot show artifact readiness.
- Recommendation usage cannot be traced to a specific package version.

Recommended fix:

- Add artifact tables with `application_id`, input summary, output JSON, created timestamp, and deterministic version.

### No migration strategy

The schema is currently maintained as a single SQL file.

Risk:

- Future schema changes become hard to apply safely.
- Existing environments may drift.
- CI cannot validate migrations.

Recommended fix:

- Add Alembic or a lightweight SQL migration convention.
- Keep `schema.sql` as a generated or bootstrap reference if useful.

### Broad modules

`main.py` and `repositories.py` are readable today but increasingly broad.

Risk:

- More features will make route and repository changes harder to review.
- Cross-domain behavior may become tangled.

Recommended fix:

- Split routers and repositories by aggregate:
  - candidates
  - jobs
  - applications
  - matching
  - packages
  - intelligence
  - outcomes

### No authentication or ownership model

The MVP is suitable for local/demo use, not real hosted personal data.

Risk:

- Any hosted deployment would expose sensitive career data without protection.

Recommended fix:

- Define user/workspace ownership before production deployment.
- Add authorization checks early in the v1 path.

## Testing debt

Current tests are useful and protect deterministic behavior. Remaining gaps:

- Real PostgreSQL repository tests.
- API route tests for all core endpoints.
- Error response tests.
- Migration tests.
- Privacy and redaction tests for broader examples.
- Application workflow tests across create, match, package, intelligence, outcome, and insight.

## Documentation debt

The README has become the single home for setup, architecture, API examples, sprint history, and guardrails.

Recommended split:

- `README.md`: project overview and quickstart.
- `docs/architecture.md`: backend and data architecture.
- `docs/api.md`: endpoint examples.
- `docs/privacy.md`: safety and data handling.
- `docs/releases.md`: sprint history.
- `docs/roadmap.md`: planned work.

## Risk-ranked backlog

High priority:

- Add migration strategy.
- Add authentication and ownership plan.
- Add response models and standard errors.
- Persist generated artifacts.
- Add status history.

Medium priority:

- Split routers and repositories.
- Add pagination and filters.
- Add live database tests.
- Improve input validation.
- Expand redaction tests.

Lower priority:

- Split README into docs.
- Add dependency scanning.
- Add generated OpenAPI review.
- Add dashboard-oriented read models after product direction is confirmed.

## Conclusion

The project does not need a rewrite. It needs a hardening sprint that turns the MVP's successful sprint layers into stable v1 foundations.
