# Private Beta Acceptance Test Plan

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Purpose

Validate that a brand-new user can install, configure, use, back up, restore, and upgrade AI-Career-OS without developer assistance.

This is a product validation milestone, not a development sprint.

## V1 Product Scope Clarification

V1 is CV-driven job matching and application preparation.

The acceptance test must prove more than a generic manual candidate workflow. It
must prove that a user can start from CV content and a vacancy, extract the
candidate and job signals, generate a credible match, receive useful CV update
recommendations, generate a cover letter draft, create an application, and track
that application in the pipeline.

Manual candidate entry is supportive, not core.

Recruiter CRM is V2 and remains out of scope for V1.

## Scope

In scope:

- Installation from `docs/production-installation.md` on current `main`
- First user registration and login
- Candidate, job, matching, package, application, outcome, pipeline, reporting, backup, restore, and upgrade workflows
- CV-driven candidate intake, extraction, matching, CV recommendations, and cover letter generation
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
- CV-driven intake and matching scenarios pass with realistic mock CV and vacancy examples
- Match percentage quality is reviewed against expected match bands
- CV update recommendations and cover letter generation are validated

## Scenario Matrix

| ID | Scenario | Expected Result |
| --- | --- | --- |
| 1 | Installation | Docker, Compose, migrations, backend, and frontend start successfully. |
| 2 | First User Registration | Register, login, logout, and login again all work. |
| 3 | Candidate Creation | Candidate profile can be created, persists, and reloads. |
| 4 | CV Import | User can paste CV text and extract candidate profile, skills, roles, experience highlights, certifications, domains, and seniority indicators. |
| 5 | Job Import | Job text and URL imports persist jobs and extract job requirements, skills, responsibilities, domains, and seniority indicators. |
| 6 | Matching | Match generation includes accurate score, weighted sub-scores, gaps, strengths, and recommendations for realistic CV/job examples. |
| 7 | CV Updates And Cover Letter | CV update recommendations and cover letter draft are generated and useful. |
| 8 | Application Lifecycle | Application moves through pipeline states with history, notes, and next actions. |
| 9 | Outcome Tracking | Outcomes are created, retrieved, and reflected in insights. |
| 10 | Reporting | Dashboard, funnel, application, outcome, skill, and recommendation analytics load. |
| 11 | Security | User A cannot access User B data. |
| 12 | Backup | Backup procedure creates a usable backup file. |
| 13 | Restore | Restore procedure preserves data and passes smoke test. |
| 14 | Upgrade | Pull, rebuild, migration, restart, and smoke test succeed. |
| 15 | Performance | Login, dashboard, and Kanban load times are recorded. |
| 16 | Usability Review | Confusing screens, unclear instructions, validations, and UX pain points are documented. |

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

### 4. CV Import

Use realistic mock CV text.

Verify:

- Paste CV text.
- Candidate profile is extracted.
- Skills are extracted.
- Roles are extracted.
- Experience highlights are extracted.
- Certifications are extracted when present.
- Domains are extracted.
- Seniority indicators are extracted.

### 5. Job Import

Verify:

- Import job from pasted text.
- Import job from safe public URL.
- Persisted jobs remain visible after refresh.
- Required skills are extracted.
- Preferred skills are extracted.
- Responsibilities are extracted.
- Domain keywords are extracted.
- Seniority indicators are extracted.

### 6. Matching

Verify:

- Generate match.
- Overall match percentage appears.
- Weighted sub-scores appear.
- Strengths appear.
- Gap analysis appears.
- Recommendations are actionable.
- Match band is plausible for the realistic CV/job fixture.

### 7. CV Updates And Cover Letter

Verify:

- Summary update suggestion appears.
- Skills section update suggestion appears.
- Experience bullet suggestions appear.
- Keyword alignment suggestions appear.
- Missing evidence warnings appear where appropriate.
- Cover letter draft appears.
- Cover letter uses candidate strengths and vacancy requirements.

### 8. Application Lifecycle

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

### 9. Outcome Tracking

Verify:

- Create outcome.
- Retrieve outcome history.
- Candidate insights update.

### 10. Reporting

Verify:

- Dashboard loads.
- Funnel metrics load.
- Application analytics load.
- Outcome analytics load.
- Skills analytics load.
- Recommendation analytics load.

### 11. Security

Create User A and User B.

Verify User A cannot access User B:

- candidates
- applications
- reporting

### 12. Backup

Follow backup instructions in `docs/production-installation.md`.

Verify:

- Backup command completes.
- Backup file exists.
- Backup file is non-empty.

### 13. Restore

Follow restore instructions in `docs/production-installation.md`.

Verify:

- Restore command completes.
- User can login after restore.
- Dashboard loads after restore.
- Application list or Kanban loads after restore.
- Previously created test data is preserved.

### 14. Upgrade

Follow upgrade instructions in `docs/production-installation.md`.

Verify:

- `git pull` succeeds.
- Containers rebuild.
- Migration runner succeeds.
- Services restart.
- Smoke test passes.

### 15. Performance

Measure:

- Login time
- Dashboard load time
- Kanban load time

### 16. Usability Review

Document:

- confusing screens
- unclear instructions
- missing validations
- UX pain points

## Legacy Generic Workflow Checks

The following checks remain useful but are no longer sufficient for V1 readiness.

### Application Package

Verify:

- Generate application package.
- Tailored summary appears.
- Cover letter draft appears.
- Talking points appear.
- Package can be retrieved or viewed again.

## Exit Criteria

Complete `PRIVATE_BETA_TEST_RESULTS.md` after execution.

If `PRIVATE_BETA_READY = YES`, recommend `v1.0.0 Private Beta Release`.

If `PRIVATE_BETA_READY = NO`, keep `V1_BLOCKERS.md` updated with required fixes.
