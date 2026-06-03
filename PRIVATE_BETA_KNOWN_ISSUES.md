# Private Beta Known Issues

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Summary

This document tracks issues discovered or identified during the Private Beta Acceptance Test milestone.

One HIGH installation configuration issue was confirmed during real acceptance
testing and fixed by standardizing PostgreSQL URLs on SQLAlchemy's psycopg v3
dialect. Sprint 14 was released as `v0.14.0` and the User Intake Wizard is now
deployed on `career-beta`, but the full browser workflow is blocked by missing
CORS middleware/configuration for the split frontend/backend deployment.

## Known Issues

| ID | Severity | Category | Status | Issue | Evidence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| PBAT-001 | High | Test Environment | Open | Clean-environment acceptance test could not be executed in the Codex environment. | Current environment is not a clean VM/laptop and Docker is unavailable. | Run the full acceptance test on a clean Windows or Linux VM/laptop with Docker. |
| PBAT-002 | High | Installation Evidence | Open | Installation has not been fully proven from current `main` on a clean machine. | The real acceptance test reached the migration runner, frontend runtime, frontend healthcheck, browser auth, and direct auth diagnostics. PBAT-009 is resolved, PBAT-010 is fixed locally, direct curl registration now passes, and PBAT-011 still needs committed VM re-test. | Execute `docs/production-installation.md` end to end again. |
| PBAT-003 | High | Backup / Restore Evidence | Open | Backup and restore have not been proven with real PostgreSQL container data. | Acceptance test stopped at migration runner before data workflows. | Run backup and restore scenarios after installation succeeds. |
| PBAT-004 | High | Security Evidence | Open | User A / User B ownership isolation has not been proven in acceptance environment. | App workflow did not reach two-user test because migration runner failed before fix. | Execute isolation test after registration and data creation. |
| PBAT-005 | Medium | Performance Evidence | Open | Login, dashboard, and Kanban timings have not been measured. | App workflow did not reach performance measurement. | Measure during clean-environment run. |
| PBAT-006 | Medium | Usability Evidence | Open | First-time user usability review has not been performed. | Workflow did not reach UI walkthrough. | Have a first-time tester execute the plan without developer assistance. |
| PBAT-007 | Low | Production Hardening | Known Limitation | `vite preview` is documented as acceptable for controlled private beta but not hardened broad production hosting. | Documented in `docs/production-installation.md`. | For broader production, serve `frontend/dist` with Nginx, Caddy, or managed static hosting. |
| PBAT-008 | Low | Security Hardening | Known Limitation | Refresh token storage remains MVP-level in `v0.13.0`. | Documented production warning. | Revisit token/session hardening before broad public SaaS launch. |
| PBAT-009 | High | Migration Runner | Resolved, Pending Full Installation Re-Run | Production migration runner failed with `ModuleNotFoundError: No module named 'psycopg2'`. | `alembic upgrade head` used a bare `postgresql://` URL, causing SQLAlchemy to attempt the default psycopg2 driver while the backend image installs psycopg v3. On `career-beta`, changing `DATABASE_URL` to `postgresql+psycopg://...` allowed Alembic to start successfully. | Resolved by standardizing documented and compose `DATABASE_URL` examples to `postgresql+psycopg://`; re-run the full production installation from the committed fix. |
| PBAT-010 | Medium | Frontend Healthcheck | Resolved on VM, Pending Committed Re-Test | Frontend container reported unhealthy although the frontend served `HTTP/1.1 200 OK`. | On `career-beta`, `docker ps` showed `ai-career-os-frontend-1 unhealthy`, while `curl -I http://127.0.0.1:3000` returned `HTTP/1.1 200 OK`. After applying the Node-based healthcheck locally on the VM, frontend healthcheck passed. | Fixed by replacing the frontend healthcheck with a Node-native `fetch()` command that works inside `node:22-alpine`; recreate frontend container from the committed branch and re-check health. |
| PBAT-011 | High | CORS | Open | Browser API calls are blocked by missing CORS middleware/configuration in split frontend/backend deployment. | `career-beta` frontend `http://192.168.1.130:3000` and backend `http://192.168.1.130:8000` are healthy, User Intake Wizard is deployed, and direct backend curl works. Browser calls fail with no `Access-Control-Allow-Origin` header. VM validation showed `.env.production` contains `CORS_ORIGINS=http://192.168.1.130:3000`, but `docker-compose.prod.yml` does not pass it and `backend/app` has no `CORSMiddleware`. | Add FastAPI `CORSMiddleware`, pass `CORS_ORIGINS` to backend in production compose, rebuild backend, and retest browser calls. |
| PBAT-012 | High | Database Diagnostics | Resolved on VM, Diagnostics Retained | Direct backend registration initially returned `503 service_unavailable` / `Database operation failed`. | After the `DATABASE_URL` runtime fix, direct backend registration passed via curl on `career-beta`. | Server-side exception logging remains in this PR for future database operation failures while API responses stay generic. |
| PBAT-013 | Medium | Guided Workflow UX | Fixed, Pending VM Re-Test | Guided beta workflow completion state did not mark `Generate Package` and `View Insights` complete. | The workflow reached `outcome recorded`, but those two chips/buttons remained grey/incomplete. | Fixed by wiring package success state, visible workflow errors, and a View Insights workflow action that marks the step complete. |
| PBAT-014 | High | Production Sync | Resolved | `career-beta` has been updated far enough to serve the Sprint 14 User Intake Wizard. | Latest VM validation confirms User Intake Wizard is deployed. | Continue with PBAT-011 CORS fix/retest before full acceptance. |
| PBAT-015 | High | Match Payload | Open | User Intake Wizard generated an invalid `/match` request payload. | Login, dashboard, candidate intake, and job text import passed on `career-beta`, but Generate Match returned `Request validation failed`. Backend `/match` expects `candidate.name`; the saved candidate object uses `display_name`. | Normalize the candidate payload before `/match` by mapping `display_name` to `name`, then re-test match score, strengths, gaps, and recommendations. |

## Critical Issues

None confirmed.

## High Issues

- PBAT-001: Clean-environment acceptance test could not be executed.
- PBAT-002: Installation not proven on clean machine.
- PBAT-003: Backup and restore not proven.
- PBAT-004: Ownership isolation not proven in acceptance environment.
- PBAT-009: Migration runner failed before fix because SQLAlchemy attempted psycopg2 instead of psycopg v3.
- PBAT-011: CORS failure blocks browser API calls in split frontend/backend deployment.
- PBAT-012: Direct auth registration initially returned 503, but now passes via curl after the runtime database fix.
- PBAT-014: Production VM sync to Sprint 14 is resolved enough for User Intake Wizard validation.
- PBAT-015: User Intake Wizard generated invalid match payload.

PBAT-009 was a confirmed installation blocker and has been fixed in this PR. It
was temporarily re-tested on `career-beta` by switching `DATABASE_URL` to
`postgresql+psycopg://...`, which allowed Alembic to start successfully. It
remains tied to PBAT-002 until the full installation is re-run from the committed
branch.

## Medium Issues

- PBAT-005: Performance baseline not measured.
- PBAT-006: First-time usability review not performed.
- PBAT-010: Frontend healthcheck failed even though frontend runtime returned 200 OK.
- PBAT-013: Guided workflow completion state did not mark package and insights steps complete.

PBAT-010 is fixed in this PR by replacing the `wget`-based frontend healthcheck
with a Node-native `fetch()` command. The fix passed locally on `career-beta`,
and still needs committed-branch re-test.

PBAT-013 is fixed in this PR by completing the guided workflow state for package
generation and insights viewing. It still needs committed-branch browser re-test.

## Low Issues

- PBAT-007: Vite preview is private-beta level only.
- PBAT-008: Refresh token/session hardening remains a future production-hardening topic.

## Required Follow-Up

1. Provision a clean Windows or Linux VM/laptop.
2. Install Docker and Docker Compose.
3. Clone current `main`.
4. Follow `docs/production-installation.md` exactly.
5. Execute all scenarios in `PRIVATE_BETA_TEST_PLAN.md`.
6. Update `PRIVATE_BETA_TEST_RESULTS.md` with actual evidence.
7. Reclassify any failed scenario as Critical, High, Medium, or Low.
8. Reassess `PRIVATE_BETA_READY`.
9. Confirm browser API calls from the Sprint 14 User Intake Wizard receive
   `Access-Control-Allow-Origin` for the configured frontend origin.
10. Confirm Generate Match succeeds and displays readable score, strengths,
    gaps, and recommendations.
