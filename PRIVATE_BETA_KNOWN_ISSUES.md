# Private Beta Known Issues

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Summary

This document tracks issues discovered or identified during the Private Beta Acceptance Test milestone.

One HIGH installation configuration issue was confirmed during real acceptance
testing and fixed by standardizing PostgreSQL URLs on SQLAlchemy's psycopg v3
dialect. The remaining blocker is that the full Docker-based production
installation and workflow have not yet been re-run from the committed fix.

## Known Issues

| ID | Severity | Category | Status | Issue | Evidence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| PBAT-001 | High | Test Environment | Open | Clean-environment acceptance test could not be executed in the Codex environment. | Current environment is not a clean VM/laptop and Docker is unavailable. | Run the full acceptance test on a clean Windows or Linux VM/laptop with Docker. |
| PBAT-002 | High | Installation Evidence | Open | Installation has not been fully proven from current `main` on a clean machine. | The real acceptance test reached the migration runner and found PBAT-009. A temporary `postgresql+psycopg://...` VM retest allowed Alembic to start successfully, but remaining workflows still need re-run from the committed fix. | Execute `docs/production-installation.md` end to end again. |
| PBAT-003 | High | Backup / Restore Evidence | Open | Backup and restore have not been proven with real PostgreSQL container data. | Acceptance test stopped at migration runner before data workflows. | Run backup and restore scenarios after installation succeeds. |
| PBAT-004 | High | Security Evidence | Open | User A / User B ownership isolation has not been proven in acceptance environment. | App workflow did not reach two-user test because migration runner failed before fix. | Execute isolation test after registration and data creation. |
| PBAT-005 | Medium | Performance Evidence | Open | Login, dashboard, and Kanban timings have not been measured. | App workflow did not reach performance measurement. | Measure during clean-environment run. |
| PBAT-006 | Medium | Usability Evidence | Open | First-time user usability review has not been performed. | Workflow did not reach UI walkthrough. | Have a first-time tester execute the plan without developer assistance. |
| PBAT-007 | Low | Production Hardening | Known Limitation | `vite preview` is documented as acceptable for controlled private beta but not hardened broad production hosting. | Documented in `docs/production-installation.md`. | For broader production, serve `frontend/dist` with Nginx, Caddy, or managed static hosting. |
| PBAT-008 | Low | Security Hardening | Known Limitation | Refresh token storage remains MVP-level in `v0.13.0`. | Documented production warning. | Revisit token/session hardening before broad public SaaS launch. |
| PBAT-009 | High | Migration Runner | Resolved, Pending Full Installation Re-Run | Production migration runner failed with `ModuleNotFoundError: No module named 'psycopg2'`. | `alembic upgrade head` used a bare `postgresql://` URL, causing SQLAlchemy to attempt the default psycopg2 driver while the backend image installs psycopg v3. On `career-beta`, changing `DATABASE_URL` to `postgresql+psycopg://...` allowed Alembic to start successfully. | Resolved by standardizing documented and compose `DATABASE_URL` examples to `postgresql+psycopg://`; re-run the full production installation from the committed fix. |

## Critical Issues

None confirmed.

## High Issues

- PBAT-001: Clean-environment acceptance test could not be executed.
- PBAT-002: Installation not proven on clean machine.
- PBAT-003: Backup and restore not proven.
- PBAT-004: Ownership isolation not proven in acceptance environment.
- PBAT-009: Migration runner failed before fix because SQLAlchemy attempted psycopg2 instead of psycopg v3.

PBAT-009 was a confirmed installation blocker and has been fixed in this PR. It
was temporarily re-tested on `career-beta` by switching `DATABASE_URL` to
`postgresql+psycopg://...`, which allowed Alembic to start successfully. It
remains tied to PBAT-002 until the full installation is re-run from the committed
branch.

## Medium Issues

- PBAT-005: Performance baseline not measured.
- PBAT-006: First-time usability review not performed.

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
