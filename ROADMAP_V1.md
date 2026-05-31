# V1 Roadmap

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Roadmap principle

AI-Career-OS should reach v1.0 as a trustworthy, deterministic career workflow system before it adds AI models, paid enrichment APIs, scraping, browser automation, or automatic applications.

The best path is:

1. Harden the architecture.
2. Add a usable application pipeline.
3. Add reporting and lightweight relationship tracking.
4. Prepare a private beta release.

## v0.9: Architecture Hardening

Goal:

Prepare the codebase and data model for real product workflows.

Recommended scope:

- Add database migration strategy.
- Split API routers by domain.
- Split repository functions by aggregate.
- Add explicit response models.
- Add standard error response model.
- Add `/v1` API versioning or define the versioning plan.
- Add application status history.
- Persist application packages as first-class artifacts.
- Persist company intelligence as first-class artifacts.
- Add live PostgreSQL integration test path.
- Add stricter request validation for free-text fields.

Acceptance criteria:

- Existing behavior remains compatible.
- Existing tests pass.
- New tests cover migrations, response models, and core application workflow.
- No new product surface beyond hardening.

## v0.10: Application Pipeline & Kanban

Goal:

Make Application the daily workflow center.

Recommended scope:

- Add pipeline-friendly application list filters.
- Add status board data endpoint.
- Add status history display data.
- Add next-action fields.
- Add follow-up due date support.
- Add application source and external application URL fields if needed.
- Add artifact readiness status for match, package, and intelligence.
- Add endpoint examples for a future dashboard.

Acceptance criteria:

- Candidate can track all applications by status.
- API supports kanban/dashboard views.
- Status transitions remain deterministic and auditable.
- No automatic applications or email sending.

## v0.11: Reporting, Insights, and Recruiter CRM Foundations

Goal:

Turn outcome tracking into practical learning and lightweight relationship management.

Recommended scope:

- Add dashboard reporting endpoints.
- Add time-windowed conversion metrics.
- Add skill performance summaries.
- Add source performance summaries.
- Add job family performance summaries.
- Add recruiter/contact preparation model only if privacy design is ready.
- Add interaction notes without storing unnecessary private contact data.
- Add recommendation usage reports.

Acceptance criteria:

- Candidate can see what is working.
- Reporting is based on deterministic calculations.
- Contact-related fields follow privacy rules.
- No scraping, LinkedIn automation, paid enrichment, or email sending.

## v1.0: Private Beta Readiness

Goal:

Release a coherent, maintainable, privacy-conscious private beta.

Recommended scope:

- Add authentication and ownership model.
- Add data export and deletion paths.
- Add deployment documentation.
- Add privacy and security documentation.
- Add end-to-end workflow tests.
- Add stable API documentation.
- Add seeded demo scenario.
- Add generated package export in markdown or plain text.
- Add operational checks for database, migrations, and configuration.

Acceptance criteria:

- A user can manage a full application pipeline from job import to outcome.
- The system protects personal career data with authentication and ownership.
- Generated outputs are deterministic and inspectable.
- The API has stable v1 documentation.
- No hidden external automation is introduced.

## Deferred until after v1

These ideas should remain out of scope until the deterministic private beta is mature:

- LLM-generated content.
- Paid company enrichment APIs.
- Browser automation.
- LinkedIn automation.
- Credential-based job board access.
- Automatic applications.
- Email sending.
- Multi-user team workflows.

## Recommended Sprint 9

Recommended next milestone: **Sprint 9: Architecture Hardening**.

Why:

- The Application entity is now central, so the foundation should be stabilized around it.
- Pipeline, reporting, and recruiter CRM work will all depend on cleaner API and data contracts.
- The project can still harden without a large migration burden.
- Privacy and persistence decisions should be made before more user-facing workflow is added.

## Success definition for v1

AI-Career-OS v1.0 should be:

- Deterministic.
- Private by design.
- Useful for a complete manual career workflow.
- Clear about what it does not automate.
- Maintainable enough for future AI or integration experiments without compromising trust.
