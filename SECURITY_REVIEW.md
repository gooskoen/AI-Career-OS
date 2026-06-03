# Security Review after v0.8.0

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Executive summary

AI-Career-OS has good early security posture for an MVP because it avoids high-risk automation and external data collection patterns. The project explicitly avoids private CV files, LinkedIn exports, recruiter contacts, API keys, cookies, session tokens, scraping, and automatic applications.

The largest security gap before real-world use is not a single code issue. It is the absence of product-level access control, retention policy, and stronger PII handling for user-entered text.

## Current guardrails

The project currently states and follows these guardrails:

- No paid API dependency.
- No LLM dependency.
- No scraping.
- No browser automation.
- No LinkedIn automation.
- No credential-based job access.
- No email sending.
- No automatic applications.
- Mock and demo data only in repository examples.
- Environment variables are used for database configuration.

These guardrails should remain part of the project definition through v1.0.

## PII handling

Current posture:

- README warns against storing private CVs, LinkedIn exports, recruiter contacts, API keys, cookies, and session tokens.
- Notes and outcome notes have basic redaction support.
- Application package and intelligence outputs are deterministic and should not require external data.

Risks:

- Free-text candidate profiles, notes, outcomes, and job imports can still contain personal data.
- Regex redaction is useful but limited. It can miss names, addresses, unusual phone formats, and sensitive context.
- There is no field-level classification for sensitive data.
- There is no retention or deletion policy.
- There is no audit trail for when sensitive records are created or changed.

Recommendations:

- Add a data classification note for each stored field.
- Add stricter max lengths and validation for free-text fields.
- Add a privacy review checklist before any UI or import expansion.
- Add a deletion/export path before real user onboarding.
- Treat notes as sensitive by default.

## Notes redaction

Current posture:

- Notes support exists and is linked to applications.
- Redaction is applied in repository paths.

Risks:

- Redaction can create a false sense of completeness.
- Notes may contain names, contact details, salary details, health information, protected characteristics, or confidential recruiter comments.
- Users may paste complete emails or private messages into notes.

Recommendations:

- Keep redaction, but document it as best-effort.
- Add visible API and README guidance that notes should not contain secrets or private contact data.
- Add future support for sensitive-note flags or encrypted note storage if real personal data is introduced.
- Add tests for more redaction examples.

## Input validation

Current posture:

- Pydantic request models provide structural validation.
- URL ingestion includes safety checks against private/local URLs and non-http schemes.
- URL downloads use timeout and size limits.

Risks:

- Many text fields do not yet appear to have strict length limits.
- Job ingestion accepts untrusted text and HTML-derived content.
- No request size policy is documented at the API level.
- No rate limiting exists.

Recommendations:

- Add max length constraints to all request models.
- Add clear validation errors for oversized input.
- Add rate limiting before public deployment.
- Add content-type and response-size enforcement to URL ingestion.
- Keep SSRF protections mandatory for all future URL features.

## Endpoint exposure

Current posture:

- MVP endpoints appear intended for local development and controlled demos.
- No authentication layer exists.

Risks:

- Without authentication, any deployed instance exposes candidate, job, application, outcome, and notes data.
- There is no authorization model for candidate ownership.
- There is no admin/user boundary.

Recommendations before real deployment:

- Add authentication.
- Add user or workspace ownership to core records.
- Add authorization checks to every candidate, application, job, outcome, and insight endpoint.
- Add CORS policy review.
- Add basic request logging that excludes sensitive body content.

## Secrets and configuration

Current posture:

- `.env.example` documents expected database variables.
- Secrets should come from environment variables.
- Repository should not contain API keys or real contacts.

Risks:

- Future integrations may pressure the project to add API credentials.
- Logs can accidentally expose `DATABASE_URL` or pasted content.

Recommendations:

- Keep `.env` ignored.
- Never log raw request bodies.
- Add deployment documentation for secret managers when production hosting is introduced.
- Keep CI free of real secrets unless required by integration tests.

## External access and scraping

Current posture:

- Manual LinkedIn import is supported.
- URL import uses simple HTTP GET and safety checks.
- No scraping, browser automation, cookies, or logged-in access are included.

Risks:

- Future feature requests may blur manual import, crawling, and automation.
- Recruiter CRM features may tempt storage of real contact data.

Recommendations:

- Preserve explicit "manual import only" language.
- Require a security/product review before any web browsing or external API expansion.
- Do not add credentialed website access without a separate threat model.

## Security technical debt

High priority:

- Add authentication and ownership before real deployment.
- Add data retention and deletion design.
- Add max length validation for free-text inputs.
- Add standard error responses that do not leak internals.

Medium priority:

- Improve redaction coverage and tests.
- Add audit events for application status and outcome changes.
- Add request logging policy.
- Add CORS and deployment hardening guidance.

Low priority:

- Add a formal privacy checklist.
- Add static security scanning in CI.
- Add dependency vulnerability scanning.

## Conclusion

The project has avoided the biggest early security mistakes by keeping the MVP deterministic, local, and automation-free. Before real user data or hosted use, the next security step is explicit access control, stronger validation, and a clearer privacy model for candidate data and notes.
