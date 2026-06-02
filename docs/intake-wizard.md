# Sprint 14: User Intake Wizard

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Purpose

The Sprint 14 intake wizard exposes the existing backend intake capabilities through a guided private beta workflow. It replaces the hardcoded demo workflow with real user-provided candidate and vacancy data.

The wizard is frontend orchestration only. It does not add resume parsing, scraping, new matching logic, AI calls, or backend business logic.

## Workflow

1. Login.
2. Create a candidate profile.
3. Import a job by pasted vacancy text or a pasted job URL.
4. Generate and review a deterministic match.
5. Generate an application package.
6. Create an application.
7. Continue through the existing application pipeline.

Progress is shown as:

Candidate -> Job -> Match -> Package -> Application

Wizard state is persisted in browser session storage while the user is logged in.

## API Mapping

| Wizard step | Endpoint | Purpose |
| --- | --- | --- |
| Candidate | `POST /candidates` | Create the authenticated user's candidate profile. |
| Job text import | `POST /jobs/import-text` | Import a pasted vacancy description into the existing job ingestion layer. |
| Job URL import | `POST /jobs/import-url` | Import a vacancy URL through the existing safe URL ingestion layer. |
| Match review | `POST /match` | Preview deterministic match details for display. |
| Persist match | `POST /matches/persist` | Store the match result for application linkage. |
| Application package | `POST /applications/package` | Generate deterministic package content from candidate, job, and match. |
| Application | `POST /applications` | Create the real application aggregate. |

`POST /match` expects this shape:

```json
{
  "candidate": {
    "name": "Candidate Name",
    "headline": "Role headline",
    "location": "Location",
    "summary": "Short profile summary",
    "target_roles": ["Target role"],
    "skills": ["Skill"],
    "experience_highlights": ["Evidence"],
    "portfolio_links": []
  },
  "job": {
    "title": "Job title",
    "company": "Company",
    "location": "Location",
    "description": "Job description",
    "required_skills": ["Required skill"],
    "nice_to_have_skills": []
  }
}
```

The frontend normalizes the saved candidate response before calling `/match`
because persisted candidate records use `display_name`, while the matching
contract expects `candidate.name`.

## Candidate Intake

The candidate form captures:

- Full name
- Headline
- Location
- Summary
- Skills
- Target roles
- Experience highlights

Skills, target roles, and experience highlights can be entered as comma-separated or newline-separated values.

## Job Intake

The wizard supports two existing backend paths:

- Paste Job Description
- Paste Job URL

URL import still follows the backend ingestion guardrails. It is not a crawler and does not bypass website terms, authentication, or access controls.

## Match Review

The match screen displays:

- Match score
- Strengths
- Gaps
- Recommended actions

The UI renders these as readable sections instead of raw JSON.

## Error Handling

The wizard displays action-specific error messages and keeps the user on the current step when an API call fails. Network/CORS failures are shown as API connectivity problems instead of a generic `Failed to fetch` browser message.

## Guardrails

Sprint 14 intentionally excludes:

- Resume/CV PDF upload
- DOCX upload
- Resume parsing
- New matching engines
- Recruiter CRM
- AI or LLM integration
- Email sending
- LinkedIn automation
- Browser automation
- Backend redesign

## Validation

Frontend tests cover:

- Candidate intake
- Job text import
- Job URL import
- Match review display
- Wizard progression
- Wizard error handling
