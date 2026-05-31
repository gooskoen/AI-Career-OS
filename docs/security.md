# Security

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Sprint 11 Security Model

Sprint 11 adds the first ownership and authentication foundation for AI-Career-OS.
The security goal is simple: private career data must be tied to a user and repository
queries must be scoped by that user.

## Private Data Boundaries

The following records are user-owned:

- candidate profiles
- applications
- application notes
- application outcomes
- persisted match results
- persisted interview briefings
- application package records
- company intelligence report records

Job descriptions remain reusable demo/job records, but application access is always
scoped through the owning candidate and application.

## Passwords and Tokens

- Passwords are stored as PBKDF2-SHA256 hashes with per-password random salts.
- Plain text passwords are never returned by the API.
- Access tokens are short-lived JWTs.
- Refresh tokens are stored as SHA-256 hashes.
- `AUTH_SECRET` is required at API startup and should be configured outside source
  control.

## Authorization Behavior

Repository functions accept `user_id` for private aggregates and apply it in SQL.
Cross-user access is treated as not found where possible. This avoids confirming
whether another user's candidate, application, note, or generated artifact exists.

## Audit Events

The `auth_audit_events` table records basic auth events:

- register
- login
- refresh

This is intentionally small and does not store device fingerprints, IP addresses, or
external identity provider data.

## Guardrails

Sprint 11 does not add:

- reporting
- recruiter CRM
- OAuth or social login
- LLM integration
- web browsing
- LinkedIn automation
- email sending
- automatic applications

## Known Limitations

- There is no account recovery flow yet.
- There is no refresh token revocation endpoint yet.
- There are no roles or organization accounts yet.
- JWT signing uses one shared secret rather than key rotation.
- Demo job records are not user-owned in this sprint.
