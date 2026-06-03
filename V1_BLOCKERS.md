# V1 Blockers

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Current Decision

PRIVATE_BETA_READY = NO

Reason: The clarified V1 product scope is CV-driven job matching and
application preparation. The current product can support a technical
end-to-end manual workflow after the remaining acceptance fixes are re-tested,
but V1 cannot be declared ready until CV import, CV signal extraction, realistic
vacancy extraction, match quality, CV update recommendations, and cover letter
quality are validated with realistic mock CV and vacancy examples.

Recruiter CRM is V2. Generic manual candidate entry remains a supportive flow,
not the core V1 value proposition.

## Required Before v1.0.0 Private Beta Release

| ID | Severity | Blocker | Required Action | Exit Criteria |
| --- | --- | --- | --- | --- |
| V1-001 | High | Clean-environment acceptance test not executed | Run `PRIVATE_BETA_TEST_PLAN.md` on a clean Windows or Linux VM/laptop with Docker. | All scenarios have PASS / FAIL / BLOCKED evidence in `PRIVATE_BETA_TEST_RESULTS.md`. |
| V1-002 | High | Migration runner failed before fix | Re-run `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head` from the committed `postgresql+psycopg://` fix. | Migration runner completes without `psycopg2` import errors using the documented committed configuration. |
| V1-003 | High | Installation not proven after migration fix | Follow `docs/production-installation.md` exactly on clean environment. | Docker, Compose startup, migrations, backend health, and frontend load pass. |
| V1-004 | High | Browser API calls blocked by missing CORS middleware/configuration | Add FastAPI `CORSMiddleware`, pass `CORS_ORIGINS` to backend in production compose, and recreate backend from the committed branch. | Browser calls from `http://192.168.1.130:3000` to `http://192.168.1.130:8000` receive `Access-Control-Allow-Origin` for the configured frontend origin. |
| V1-005 | High | Browser auth not re-tested after CORS fix | Re-run browser register/login from `http://192.168.1.130:3000` against backend `http://192.168.1.130:8000`. | Browser registration/login succeed and no longer fail with missing `Access-Control-Allow-Origin`. |
| V1-006 | High | Backup and restore not proven | Execute backup and restore scenarios with real PostgreSQL container data. | Backup file exists, restore completes, login/dashboard/application list work after restore. |
| V1-007 | High | Ownership isolation not proven | Execute User A / User B data isolation scenario. | User A cannot access User B candidates, applications, or reporting. |
| V1-008 | High | Upgrade path not proven | Execute documented upgrade flow. | `git pull`, rebuild, migration runner, restart, and smoke test pass. |
| V1-009 | Medium | Guided workflow completion state not re-tested | Re-run guided beta workflow through package generation, insights, pipeline movement, and outcome recording. | Generate Package, View Insights, and Record Outcome all show completed only after their own successful actions. |
| V1-010 | Medium | Performance baseline not measured | Measure login, dashboard, and Kanban load times. | Timings are recorded and reviewed for private beta suitability. |
| V1-011 | Medium | First-time usability review not completed | Have a first-time tester complete the workflow without developer help. | Usability findings are captured and triaged. |
| V1-012 | High | User Intake Wizard match request invalid | Normalize the frontend `/match` payload so saved candidate `display_name` is sent as required `candidate.name`. | Generate Match succeeds after candidate intake and job import, and the UI displays score, strengths, gaps, and recommendations. |
| V1-013 | High | CV import missing | Add CV text intake as the primary V1 entry point. | User can paste realistic mock CV text and start the matching workflow from it. |
| V1-014 | High | Skills extraction from CV missing | Extract skills, roles, experience highlights, certifications, domains, and seniority indicators from CV text. | Extracted profile signals match expected fixture outputs for realistic mock CVs. |
| V1-015 | High | Vacancy skill extraction quality not validated | Validate vacancy extraction for required skills, preferred skills, responsibilities, domains, and seniority indicators. | Realistic vacancy fixtures produce expected extracted requirement signals. |
| V1-016 | High | Match percentage quality not validated | Validate match percentage and weighted sub-scores against realistic CV/job examples. | Strong, moderate, and weak fixture pairs land in expected match bands with explainable sub-scores. |
| V1-017 | High | CV update recommendations not validated | Generate and validate deterministic CV update suggestions from match gaps and job requirements. | Suggestions include summary, skills, experience bullet, keyword alignment, and missing evidence guidance. |
| V1-018 | High | Cover letter generation not validated | Generate and validate deterministic cover letter drafts from candidate, vacancy, strengths, and gaps. | Cover letter draft is professional, specific to the vacancy, and does not leak private or unrelated data. |

## Clarified V1 Product Blockers

The following blockers supersede a purely technical private beta readiness
decision:

- CV import is not available as a first-class V1 workflow.
- CV skills and experience signal extraction are not implemented.
- Vacancy extraction quality has not been validated with realistic job
  descriptions.
- Match percentage quality has not been validated against known strong,
  moderate, and weak CV/job examples.
- CV update recommendations have not been validated for usefulness.
- Cover letter generation has not been validated against realistic CV/job input.

These are product-scope blockers, not infrastructure blockers. They should be
handled in Sprint 15 before any `v1.0.0` private beta recommendation.

## Confirmed Product Blockers

The migration runner driver mismatch was confirmed during acceptance testing:

- Command: `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head`
- Failure: `ModuleNotFoundError: No module named 'psycopg2'`
- Root cause: bare `postgresql://` URL caused SQLAlchemy/Alembic to attempt the default psycopg2 driver.
- Fix in this PR: production and compose examples now use `postgresql+psycopg://` for psycopg v3.
- Temporary retest: on `career-beta`, switching `DATABASE_URL` to `postgresql+psycopg://...` allowed Alembic to start successfully and removed the `psycopg2` import failure.
- Additional findings: browser auth was blocked by missing CORS preflight support. Direct `POST /auth/register` now passes via curl after the `DATABASE_URL` runtime fix.
- Fix in this PR: configurable FastAPI CORS support, structured server-side database operation logging, and guided workflow completion-state fixes.
- Sprint 14 release: PR #18 was merged, tag `v0.14.0` exists remotely, and User Intake Wizard is deployed on `career-beta`.
- Remaining blockers: fix CORS for the split frontend/backend deployment, fix the User Intake Wizard `/match` payload, then re-test the full installation and registration workflow.

No data-loss defect, authentication defect, or ownership defect has been confirmed yet.

## Not Required Before Controlled Private Beta Unless Found During Testing

The following are future hardening areas, but they should not block controlled private beta unless the acceptance test exposes a critical risk:

- Broad public SaaS hosting hardening
- Recruiter CRM
- AI/LLM expansion
- Email sending
- LinkedIn automation
- Advanced observability
- Advanced session/token revocation model

## v1.0.0 Release Recommendation

Do not tag or announce `v1.0.0 Private Beta Release` until:

- No critical defects remain.
- No data-loss defects remain.
- No authentication defects remain.
- No ownership defects remain.
- No installation blockers remain.
- Backup and restore pass.
- At least 90% of acceptance scenarios pass.

When those technical and CV-driven product conditions are met, update
`PRIVATE_BETA_TEST_RESULTS.md` to:

```text
PRIVATE_BETA_READY = YES
```

Then recommend:

```text
v1.0.0 Private Beta Release
```

Current recommendation:

```text
Do not tag v1.0.0 yet.
First complete Sprint 15 CV-driven intake and matching quality work, then
re-run the clean-environment acceptance test against realistic CV/job fixtures.
```
