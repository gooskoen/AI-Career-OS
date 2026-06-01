# Private Beta Known Issues

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Summary

This document tracks issues discovered or identified during the Private Beta Acceptance Test milestone.

No product defects have been confirmed yet. The current blocker is that the available execution environment cannot run the Docker-based production installation path.

## Known Issues

| ID | Severity | Category | Status | Issue | Evidence | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| PBAT-001 | High | Test Environment | Open | Clean-environment acceptance test could not be executed. | Current environment is not a clean VM/laptop and Docker is unavailable. | Run the full acceptance test on a clean Windows or Linux VM/laptop with Docker. |
| PBAT-002 | High | Installation Evidence | Open | Installation has not been proven from current `main` on a clean machine. | `docker --version` and `docker compose version` failed before installation could begin. | Execute `docs/production-installation.md` end to end on clean environment. |
| PBAT-003 | High | Backup / Restore Evidence | Open | Backup and restore have not been proven with real PostgreSQL container data. | PostgreSQL could not be started without Docker. | Run backup and restore scenarios after installation succeeds. |
| PBAT-004 | High | Security Evidence | Open | User A / User B ownership isolation has not been proven in acceptance environment. | App could not be started, so two-user test could not run. | Execute isolation test after registration and data creation. |
| PBAT-005 | Medium | Performance Evidence | Open | Login, dashboard, and Kanban timings have not been measured. | App could not be started. | Measure during clean-environment run. |
| PBAT-006 | Medium | Usability Evidence | Open | First-time user usability review has not been performed. | No tester walkthrough possible without running app. | Have a first-time tester execute the plan without developer assistance. |
| PBAT-007 | Low | Production Hardening | Known Limitation | `vite preview` is documented as acceptable for controlled private beta but not hardened broad production hosting. | Documented in `docs/production-installation.md`. | For broader production, serve `frontend/dist` with Nginx, Caddy, or managed static hosting. |
| PBAT-008 | Low | Security Hardening | Known Limitation | Refresh token storage remains MVP-level in `v0.13.0`. | Documented production warning. | Revisit token/session hardening before broad public SaaS launch. |

## Critical Issues

None confirmed.

## High Issues

- PBAT-001: Clean-environment acceptance test could not be executed.
- PBAT-002: Installation not proven on clean machine.
- PBAT-003: Backup and restore not proven.
- PBAT-004: Ownership isolation not proven in acceptance environment.

These are evidence blockers, not confirmed product defects.

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
