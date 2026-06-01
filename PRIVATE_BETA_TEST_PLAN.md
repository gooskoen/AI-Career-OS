# Private Beta Acceptance Test Plan

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Purpose

Validate that a brand-new user can install, configure, use, back up, restore, and upgrade AI-Career-OS without developer assistance.

This is a product validation milestone, not a development sprint.

## Scope

In scope:

- Installation from `docs/production-installation.md` on current `main`
- First user registration and login
- Candidate, job, matching, package, application, outcome, pipeline, reporting, backup, restore, and upgrade workflows
- Cross-user ownership isolation
- Basic performance timing
- Usability review

Out of scope:

- Product features
- Architecture changes
- New APIs
- AI or LLM features
- Email sending
- Recruiter CRM
- LinkedIn automation

## Test Environment

Use one clean environment:

- Option A: Clean Windows VM
- Option B: Clean Windows laptop
- Option C: Clean Linux VM

Recommended first run:

- Clean Ubuntu 24.04 VM
- 2 CPU cores minimum
- 4 GB RAM minimum
- 20 GB free disk minimum
- Docker and Docker Compose installed during the test
- Fresh clone of `gooskoen/AI-Career-OS`
- No existing AI-Career-OS Docker volumes

## Test Data Rules

Use mock/demo data only.

Do not use:

- private CV files
- LinkedIn exports
- real recruiter contacts
- real API keys
- reused personal passwords
- production personal data

## Evidence To Capture

For every scenario, capture:

- PASS / FAIL / BLOCKED
- exact commands used
- observed output or behavior
- screenshots if available
- logs for failures
- workaround notes
- severity for defects

Severity levels:

- Critical: install, auth, ownership, data-loss, backup/restore, or persistence blocker.
- High: core private beta workflow blocked with no simple workaround.
- Medium: important workflow or usability problem with a workaround.
- Low: polish, copy, or minor documentation issue.

## Success Criteria

Private Beta Ready if:

- No critical defects
- No data-loss defects
- No authentication defects
- No ownership defects
- No installation blockers
- Backup and restore pass
- At least 90% of acceptance scenarios pass

## Scenario Matrix

| ID | Scenario | Expected Result |
| --- | --- | --- |
| 1 | Installation | Docker, Compose, migrations, backend, and frontend start successfully. |
| 2 | First User Registration | Register, login, logout, and login again all work. |
| 3 | Candidate Creation | Candidate profile can be created, persists, and reloads. |
| 4 | Job Import | Job text and URL imports persist jobs. |
| 5 | Matching | Match generation includes score, gaps, and recommendations. |
| 6 | Application Package | Package generation and retrieval work. |
| 7 | Application Lifecycle | Application moves through pipeline states with history, notes, and next actions. |
| 8 | Outcome Tracking | Outcomes are created, retrieved, and reflected in insights. |
| 9 | Reporting | Dashboard, funnel, application, outcome, skill, and recommendation analytics load. |
| 10 | Security | User A cannot access User B data. |
| 11 | Backup | Backup procedure creates a usable backup file. |
| 12 | Restore | Restore procedure preserves data and passes smoke test. |
| 13 | Upgrade | Pull, rebuild, migration, restart, and smoke test succeed. |
| 14 | Performance | Login, dashboard, and Kanban load times are recorded. |
| 15 | Usability Review | Confusing screens, unclear instructions, validations, and UX pain points are documented. |

## Detailed Scenarios

### 1. Installation

Follow `docs/production-installation.md` from a clean machine.

Verify:

- Docker installation succeeds.
- Docker Compose is available.
- `.env.production` can be created.
- `AUTH_SECRET` can be generated.
- Compose startup succeeds.
- Migration runner succeeds.
- Backend health returns `{"status":"ok"}`.
- Frontend loads.

### 2. First User Registration

Verify:

- Register a new user.
- Login succeeds.
- Logout succeeds.
- Login again succeeds.

### 3. Candidate Creation

Verify:

- Create candidate profile with mock data.
- Refresh page.
- Candidate profile persists and reloads.

### 4. Job Import

Verify:

- Import job from pasted text.
- Import job from safe public URL.
- Persisted jobs remain visible after refresh.

### 5. Matching

Verify:

- Generate match.
- Structured score appears.
- Gap analysis appears.
- Recommendations are actionable.

### 6. Application Package

Verify:

- Generate application package.
- Tailored summary appears.
- Cover letter draft appears.
- Talking points appear.
- Package can be retrieved or viewed again.

### 7. Application Lifecycle

Create an application and move through:

- drafted
- applied
- recruiter_replied
- interview_scheduled
- interview_completed
- offer_received

Verify:

- Status history is preserved.
- Next action can be set.
- Follow-up date can be set.
- Notes can be added.
- Summary reflects current state.

### 8. Outcome Tracking

Verify:

- Create outcome.
- Retrieve outcome history.
- Candidate insights update.

### 9. Reporting

Verify:

- Dashboard loads.
- Funnel metrics load.
- Application analytics load.
- Outcome analytics load.
- Skills analytics load.
- Recommendation analytics load.

### 10. Security

Create User A and User B.

Verify User A cannot access User B:

- candidates
- applications
- reporting

### 11. Backup

Follow backup instructions in `docs/production-installation.md`.

Verify:

- Backup command completes.
- Backup file exists.
- Backup file is non-empty.

### 12. Restore

Follow restore instructions in `docs/production-installation.md`.

Verify:

- Restore command completes.
- User can login after restore.
- Dashboard loads after restore.
- Application list or Kanban loads after restore.
- Previously created test data is preserved.

### 13. Upgrade

Follow upgrade instructions in `docs/production-installation.md`.

Verify:

- `git pull` succeeds.
- Containers rebuild.
- Migration runner succeeds.
- Services restart.
- Smoke test passes.

### 14. Performance

Measure:

- Login time
- Dashboard load time
- Kanban load time

### 15. Usability Review

Document:

- confusing screens
- unclear instructions
- missing validations
- UX pain points

## Exit Criteria

Complete `PRIVATE_BETA_TEST_RESULTS.md` after execution.

If `PRIVATE_BETA_READY = YES`, recommend `v1.0.0 Private Beta Release`.

If `PRIVATE_BETA_READY = NO`, keep `V1_BLOCKERS.md` updated with required fixes.
