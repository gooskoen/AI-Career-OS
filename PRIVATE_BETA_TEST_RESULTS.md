# Private Beta Acceptance Test Results

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Execution Summary

Repository: `gooskoen/AI-Career-OS`

Milestone: Private Beta Acceptance Test

Base under test: current `main` after PR #16 merge, commit `28c482a71837c6f6bd574037040871491a0f18f9`

Documentation under test:

- `docs/production-installation.md`
- `docker-compose.prod.yml`

Execution status: FAIL before fix, partial VM re-test passed

Reason: A real Docker-capable Private Beta Acceptance Test reached the documented
migration command and failed before the application runtime workflows could begin.
On the clean VM `career-beta`, changing `DATABASE_URL` from `postgresql://...`
to `postgresql+psycopg://...` allowed Alembic to start successfully and removed
the `psycopg2` import failure. The available Codex environment still does not
have Docker installed, so the full installation workflow cannot be re-run from
this session.

This is a confirmed installation blocker found during acceptance testing and fixed
in this PR by aligning production `DATABASE_URL` examples with SQLAlchemy's
psycopg v3 dialect.

## Environment Checked

Current execution environment:

- Windows PowerShell environment inside existing repository workspace
- Not a clean VM or clean laptop
- Docker unavailable
- Existing local repository has unrelated untracked markdown files outside this PR

Exact commands executed:

```powershell
docker --version
```

Observed result:

```text
The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

Exact commands executed:

```powershell
docker compose version
```

Observed result:

```text
The term 'docker' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

GitHub checks:

- PR #16 was confirmed merged into `main`.
- `docs/production-installation.md` exists on `main`.
- `docker-compose.prod.yml` exists on `main`.
- PR #17 was retargeted/recreated on `main`.

## Real Docker Acceptance Finding

Exact command executed on Docker-capable acceptance machine:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head
```

Observed result before fix:

```text
ModuleNotFoundError: No module named 'psycopg2'
```

Root cause:

- `.env.example` and `docs/production-installation.md` used `postgresql://...`.
- Alembic runs through SQLAlchemy.
- SQLAlchemy interpreted the bare PostgreSQL URL with the default PostgreSQL driver path and attempted to load `psycopg2`.
- The backend image intentionally installs modern psycopg v3 via `psycopg[binary]`, not `psycopg2-binary`.

Fix applied:

- Updated `.env.example` to use `postgresql+psycopg://...`.
- Updated the default `docker-compose.yml` `DATABASE_URL` fallback to use `postgresql+psycopg://...`.
- Updated `docs/production-installation.md` to use `postgresql+psycopg://...`.
- Updated `docs/migrations.md` to document that Alembic uses SQLAlchemy with the psycopg v3 dialect.
- Added a lightweight configuration test to prevent production examples from regressing to bare `postgresql://`.

Temporary VM workaround:

```text
DATABASE_URL=postgresql+psycopg://...
```

Retest result on `career-beta`:

```text
Alembic started successfully. The psycopg2 import error no longer occurred.
```

Required committed fix:

- Keep all active documented and compose `DATABASE_URL` examples on the psycopg v3 SQLAlchemy dialect.
- Re-run the full installation and workflow scenarios from the committed PR branch.

Status after fix:

```text
PSYCOG2 IMPORT ERROR RESOLVED BY TEMPORARY VM RETEST
FULL INSTALLATION WORKFLOW STILL PENDING
```

## Scenario Results

| ID | Scenario | Status | Evidence Notes | Workaround / Next Step |
| --- | --- | --- | --- | --- |
| 1 | Installation | FAIL | Migration runner failed before fix with `ModuleNotFoundError: No module named 'psycopg2'` because production `DATABASE_URL` examples used bare `postgresql://`. Temporary VM retest with `postgresql+psycopg://...` allowed Alembic to start successfully. | Re-run the full installation from the committed PR branch after the `postgresql+psycopg://` fix. |
| 2 | First User Registration | BLOCKED | Frontend/backend stack could not be started because migration failed before fix. | Run after installation passes. |
| 3 | Candidate Creation | BLOCKED | Requires authenticated running app. | Run after login passes. |
| 4 | Job Import | BLOCKED | Requires running backend/frontend. | Run after installation passes. |
| 5 | Matching | BLOCKED | Requires candidate and job setup. | Run after candidate/job workflows pass. |
| 6 | Application Package | BLOCKED | Requires match result and running app. | Run after matching passes. |
| 7 | Application Lifecycle | BLOCKED | Requires application creation and pipeline API/UI. | Run after package/application setup. |
| 8 | Outcome Tracking | BLOCKED | Requires application workflow. | Run after lifecycle scenario. |
| 9 | Reporting | BLOCKED | Requires populated runtime data. | Run after outcomes exist. |
| 10 | Security | BLOCKED | Requires two running authenticated users. | Run User A/User B isolation after installation. |
| 11 | Backup | BLOCKED | Requires live PostgreSQL container and completed installation. | Run after data exists in PostgreSQL. |
| 12 | Restore | BLOCKED | Requires backup artifact and live PostgreSQL container. | Run after backup passes. |
| 13 | Upgrade | BLOCKED | Requires deployed app and Docker Compose. | Run after initial deployment passes. |
| 14 | Performance | BLOCKED | Requires browser access to running app. | Measure after app is running. |
| 15 | Usability Review | BLOCKED | Requires first-time user walkthrough. | Assign tester with clean environment. |

## Pass / Fail Summary

| Metric | Count |
| --- | ---: |
| Total scenarios | 15 |
| PASS | 0 |
| FAIL | 1 |
| BLOCKED | 14 |
| NOT RUN | 0 |

Pass rate: 0%

The pass rate remains 0% because the installation scenario has not been fully
re-run from the committed PR branch. The specific `psycopg2` import failure was
re-tested on `career-beta` and resolved by using `postgresql+psycopg://...`.

## Discovered Defects

One installation defect was confirmed during the real Docker acceptance test.

Confirmed issues:

| ID | Severity | Area | Finding | Evidence |
| --- | --- | --- | --- | --- |
| PBAT-ENV-001 | High | Test Environment | Docker is unavailable in the current Codex environment. | `docker --version` and `docker compose version` both failed because `docker` was not recognized. |
| PBAT-009 | High | Migration Runner | Alembic migration runner attempted to load `psycopg2`. | `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head` failed with `ModuleNotFoundError: No module named 'psycopg2'`; temporary VM retest with `postgresql+psycopg://...` allowed Alembic to start successfully. |

## Issues Encountered

- Docker is not installed or not available on PATH in the Codex environment.
- The Codex environment is not clean, so it does not meet the acceptance test environment requirement.
- The Docker-capable acceptance machine found a migration driver mismatch before the app could start.
- No screenshots were captured in this session because the app could not be started here.

## Workaround Notes

Use a clean VM/laptop for the real acceptance run:

1. Pull the updated PR branch containing the `postgresql+psycopg://` fix.
2. Re-run the documented migration command on the Docker-capable machine using the committed examples.
3. If migration still starts successfully, continue the acceptance workflow from registration onward.
4. Record evidence for every scenario in this file.

## Performance Results

| Metric | Result | Notes |
| --- | --- | --- |
| Login time | BLOCKED | App could not be started. |
| Dashboard load time | BLOCKED | App could not be started. |
| Kanban load time | BLOCKED | App could not be started. |

## Usability Findings

No product usability findings were captured because the app could not be installed or opened in this environment.

The acceptance run should still capture:

- confusing screens
- unclear instructions
- missing validations
- unclear error messages
- setup friction
- places where tester needed developer knowledge

## Security Findings

No auth or ownership defect was confirmed.

Security validation remains blocked until the app runs and two-user isolation can be tested.

Required follow-up:

- User A cannot access User B candidates.
- User A cannot access User B applications.
- User A cannot access User B reporting.

## Backup / Restore Findings

Backup and restore were not executed because PostgreSQL could not be started without Docker.

Required follow-up:

- Create backup file.
- Verify backup file is non-empty.
- Restore backup.
- Confirm login works after restore.
- Confirm dashboard loads after restore.
- Confirm application list or Kanban loads after restore.
- Confirm test data is preserved.

## Remediation Recommendations

1. Re-run installation on a Docker-capable acceptance machine after this fix.
2. Keep PR #17 draft until actual scenario evidence is captured.
3. Do not tag `v1.0.0` until installation, backup, restore, ownership, and at least 90% of scenarios pass.
4. If another scenario fails, convert it into a concrete defect in `PRIVATE_BETA_KNOWN_ISSUES.md` and update `V1_BLOCKERS.md`.

## Final Decision

PRIVATE_BETA_READY = NO

Reason: Installation failed before fix, and only the migration-driver issue has
been re-tested successfully through the temporary VM workaround. No full
clean-environment pass evidence exists yet.

Recommendation: Do not declare `v1.0.0 Private Beta Release` until the clean-environment acceptance run passes the success criteria.
