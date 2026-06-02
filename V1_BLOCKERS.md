# V1 Blockers

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Current Decision

PRIVATE_BETA_READY = NO

Reason: The formal clean-environment Private Beta Acceptance Test found
production blockers in migration configuration, browser CORS, and direct auth
database behavior. The migration driver mismatch and frontend healthcheck were
fixed locally on `career-beta`, but the full installation and workflow still
need to be re-run from the committed fix.

## Required Before v1.0.0 Private Beta Release

| ID | Severity | Blocker | Required Action | Exit Criteria |
| --- | --- | --- | --- | --- |
| V1-001 | High | Clean-environment acceptance test not executed | Run `PRIVATE_BETA_TEST_PLAN.md` on a clean Windows or Linux VM/laptop with Docker. | All scenarios have PASS / FAIL / BLOCKED evidence in `PRIVATE_BETA_TEST_RESULTS.md`. |
| V1-002 | High | Migration runner failed before fix | Re-run `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head` from the committed `postgresql+psycopg://` fix. | Migration runner completes without `psycopg2` import errors using the documented committed configuration. |
| V1-003 | High | Installation not proven after migration fix | Follow `docs/production-installation.md` exactly on clean environment. | Docker, Compose startup, migrations, backend health, and frontend load pass. |
| V1-004 | High | Browser auth blocked by CORS before fix | Set `CORS_ORIGINS` to the frontend browser origin and recreate backend from the committed branch. | Browser registration/login no longer show `Failed to fetch`; preflight requests succeed. |
| V1-005 | High | Direct auth registration returns 503 | Verify migrations, inspect new backend database diagnostics, and re-run `POST /auth/register`. | Registration succeeds or a concrete database defect is documented with server-side evidence. |
| V1-006 | High | Backup and restore not proven | Execute backup and restore scenarios with real PostgreSQL container data. | Backup file exists, restore completes, login/dashboard/application list work after restore. |
| V1-007 | High | Ownership isolation not proven | Execute User A / User B data isolation scenario. | User A cannot access User B candidates, applications, or reporting. |
| V1-008 | High | Upgrade path not proven | Execute documented upgrade flow. | `git pull`, rebuild, migration runner, restart, and smoke test pass. |
| V1-009 | Medium | Performance baseline not measured | Measure login, dashboard, and Kanban load times. | Timings are recorded and reviewed for private beta suitability. |
| V1-010 | Medium | First-time usability review not completed | Have a first-time tester complete the workflow without developer help. | Usability findings are captured and triaged. |

## Confirmed Product Blockers

The migration runner driver mismatch was confirmed during acceptance testing:

- Command: `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head`
- Failure: `ModuleNotFoundError: No module named 'psycopg2'`
- Root cause: bare `postgresql://` URL caused SQLAlchemy/Alembic to attempt the default psycopg2 driver.
- Fix in this PR: production and compose examples now use `postgresql+psycopg://` for psycopg v3.
- Temporary retest: on `career-beta`, switching `DATABASE_URL` to `postgresql+psycopg://...` allowed Alembic to start successfully and removed the `psycopg2` import failure.
- Additional findings: browser auth was blocked by missing CORS preflight support, and direct `POST /auth/register` returned `503 service_unavailable` / `Database operation failed`.
- Fix in this PR: configurable FastAPI CORS support plus structured server-side database operation logging.
- Remaining blocker: re-test the full installation and registration workflow from the committed PR branch.

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

When those conditions are met, update `PRIVATE_BETA_TEST_RESULTS.md` to:

```text
PRIVATE_BETA_READY = YES
```

Then recommend:

```text
v1.0.0 Private Beta Release
```
