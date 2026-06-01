# V1 Blockers

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Current Decision

PRIVATE_BETA_READY = NO

Reason: The formal clean-environment Private Beta Acceptance Test is blocked in the current environment because Docker is unavailable. No product defect has been confirmed yet.

## Required Before v1.0.0 Private Beta Release

| ID | Severity | Blocker | Required Action | Exit Criteria |
| --- | --- | --- | --- | --- |
| V1-001 | High | Clean-environment acceptance test not executed | Run `PRIVATE_BETA_TEST_PLAN.md` on a clean Windows or Linux VM/laptop with Docker. | All scenarios have PASS / FAIL / BLOCKED evidence in `PRIVATE_BETA_TEST_RESULTS.md`. |
| V1-002 | High | Installation not proven from current `main` | Follow `docs/production-installation.md` exactly on clean environment. | Docker, Compose startup, migrations, backend health, and frontend load pass. |
| V1-003 | High | Backup and restore not proven | Execute backup and restore scenarios with real PostgreSQL container data. | Backup file exists, restore completes, login/dashboard/application list work after restore. |
| V1-004 | High | Ownership isolation not proven | Execute User A / User B data isolation scenario. | User A cannot access User B candidates, applications, or reporting. |
| V1-005 | High | Upgrade path not proven | Execute documented upgrade flow. | `git pull`, rebuild, migration runner, restart, and smoke test pass. |
| V1-006 | Medium | Performance baseline not measured | Measure login, dashboard, and Kanban load times. | Timings are recorded and reviewed for private beta suitability. |
| V1-007 | Medium | First-time usability review not completed | Have a first-time tester complete the workflow without developer help. | Usability findings are captured and triaged. |

## No Confirmed Product Blockers Yet

No critical product defect, data-loss defect, authentication defect, or ownership defect has been confirmed.

The current blockers are acceptance-evidence blockers caused by the lack of a suitable clean Docker environment in this execution context.

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
