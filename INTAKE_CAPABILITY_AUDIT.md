# Intake Capability Audit

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Scope

Repository: `gooskoen/AI-Career-OS`

Goal: determine whether real candidate/CV and job intake capabilities already exist
in the backend and whether Sprint 13 simply failed to expose them in the UX layer.

Audit date: 2026-06-02

## Executive Finding

AI-Career-OS already has backend support for structured candidate profile creation,
manual job description paste/import, safe job URL import, persisted matching, and
optional match creation during job import.

It does not currently have CV file upload, PDF parsing, DOCX parsing, resume
parsing, or free-form pasted CV text extraction into a candidate profile.

Sprint 13 exposes only a guided demo-style candidate creation and job import flow.
It does not expose the full backend intake surface as real user-facing forms.

Recommendation: use Option A for job intake and structured candidate intake
because those backend capabilities already exist. Use Option B for CV PDF/DOCX
upload and pasted CV text parsing because those capabilities are missing.

## Search Summary

Searched for:

- CV upload endpoints
- resume parsing
- candidate import
- job import
- job URL import
- job description ingestion
- raw text intake
- PDF/DOCX handling

Relevant files found:

- `backend/app/routers/candidates.py`
- `backend/app/routers/jobs.py`
- `backend/app/routers/matching.py`
- `backend/app/schemas.py`
- `backend/app/ingestion.py`
- `backend/app/repositories/candidates.py`
- `backend/app/repositories/jobs.py`
- `frontend/src/api.ts`
- `frontend/src/App.tsx`
- `README.md`
- `docs/api.md`

No PDF/DOCX upload, multipart upload, resume parser, or CV text parser endpoint was
found.

## Backend Capabilities Found

### Candidate Profile Creation

Status: active

Endpoint:

```text
POST /candidates
```

Authentication:

- Required.
- Candidate profiles are scoped to the authenticated user.

Request format:

```json
{
  "name": "Demo Candidate",
  "headline": "AI Operations Candidate",
  "location": "Remote",
  "summary": "Short candidate summary.",
  "target_roles": ["AI Operations Lead"],
  "skills": ["Python", "SQL", "workflow automation"],
  "experience_highlights": ["Built reporting workflows."],
  "portfolio_links": []
}
```

Response format:

The backend returns the inserted database row from `candidate_profiles`, including
fields such as:

```json
{
  "id": "<candidate-id>",
  "user_id": "<user-id>",
  "display_name": "Demo Candidate",
  "headline": "AI Operations Candidate",
  "location": "Remote",
  "summary": "Short candidate summary.",
  "target_roles": ["AI Operations Lead"],
  "skills": ["Python", "SQL", "workflow automation"],
  "experience_highlights": ["Built reporting workflows."],
  "portfolio_links": [],
  "created_at": "<timestamp>"
}
```

Notes:

- This is structured profile intake, not CV parsing.
- The schema uses `name` on input and stores it as `display_name`.
- No uploaded files are accepted.

### Candidate Profile Listing

Status: active

Endpoint:

```text
GET /candidates
```

Authentication:

- Required.
- Results are scoped to the authenticated user.

Request format:

- No body.

Response format:

```json
[
  {
    "id": "<candidate-id>",
    "user_id": "<user-id>",
    "display_name": "Demo Candidate",
    "headline": "AI Operations Candidate",
    "location": "Remote",
    "summary": "Short candidate summary.",
    "target_roles": ["AI Operations Lead"],
    "skills": ["Python", "SQL"],
    "experience_highlights": ["Built reporting workflows."],
    "portfolio_links": [],
    "created_at": "<timestamp>"
  }
]
```

### Demo Candidate

Status: active, demo-only

Endpoint:

```text
GET /demo/candidate
```

Authentication:

- Not required.

Request format:

- No body.

Response format:

Returns the checked-in mock profile from
`examples/candidate_profile.example.json` as a `CandidateProfile`.

Notes:

- This is not real intake.
- It is useful for demos and tests only.

### Direct Job Creation

Status: active

Endpoint:

```text
POST /jobs
```

Authentication:

- Not currently required by the router.

Request format:

```json
{
  "title": "AI Operations Lead",
  "company": "ExampleTech",
  "location": "Remote",
  "description": "Lead workflow automation and reporting.",
  "required_skills": ["Python", "SQL"],
  "nice_to_have_skills": ["FastAPI"],
  "source": null,
  "source_url": null,
  "external_id": null
}
```

Response format:

The backend returns the inserted `job_descriptions` database row.

Status note:

- Active, but less suitable for user-facing import than `/jobs/import-text`
  because it expects already structured job fields.

### Job Listing

Status: active

Endpoint:

```text
GET /jobs
```

Authentication:

- Not currently required by the router.

Request format:

- No body.

Response format:

```json
[
  {
    "id": "<job-id>",
    "title": "AI Operations Lead",
    "company": "ExampleTech",
    "location": "Remote",
    "description": "Lead workflow automation and reporting.",
    "required_skills": ["Python", "SQL"],
    "nice_to_have_skills": ["FastAPI"],
    "source": null,
    "source_url": null,
    "external_id": null,
    "created_at": "<timestamp>",
    "imported_at": "<timestamp>"
  }
]
```

### Job Text Import

Status: active

Endpoint:

```text
POST /jobs/import-text
```

Authentication:

- Required.

Request format:

```json
{
  "raw_text": "AI Operations Lead\nExampleTech\nRemote\nRequired skills: Python, SQL, workflow automation",
  "source_url": "https://www.linkedin.com/jobs/view/4242424242/",
  "match_candidate_id": "<candidate-id>"
}
```

Fields:

- `raw_text`: required string, 1 to 20,000 characters.
- `source_url`: optional string.
- `match_candidate_id`: optional UUID.

Response format:

```json
{
  "job": {
    "id": "<job-id>",
    "title": "AI Operations Lead",
    "company": "ExampleTech",
    "location": "Remote",
    "description": "AI Operations Lead\nExampleTech\nRemote\nRequired skills: Python, SQL, workflow automation",
    "required_skills": ["python", "sql", "workflow automation"],
    "nice_to_have_skills": [],
    "source": "linkedin",
    "source_url": "https://www.linkedin.com/jobs/view/4242424242/",
    "external_id": "4242424242",
    "imported_at": "<timestamp>"
  },
  "duplicate": false,
  "match": {
    "id": "<match-id>"
  }
}
```

Notes:

- The job extraction is deterministic.
- LinkedIn support is manual paste/import only.
- If `source_url` is LinkedIn, `source = "linkedin"` and `external_id` can be
  extracted from the URL.
- Duplicate detection uses `source_url` first, then company/title/location.
- If `match_candidate_id` is supplied, the endpoint creates a persisted match for
  that authenticated user's candidate.

### Job URL Import

Status: active

Endpoint:

```text
POST /jobs/import-url
```

Authentication:

- Required.

Request format:

```json
{
  "url": "https://example.com/jobs/ai-operations-lead",
  "match_candidate_id": "<candidate-id>"
}
```

Response format:

Same shape as `/jobs/import-text`:

```json
{
  "job": {
    "id": "<job-id>",
    "title": "AI Operations Lead",
    "company": "Unknown",
    "location": null,
    "description": "Readable text extracted from URL response.",
    "required_skills": ["python", "sql"],
    "nice_to_have_skills": [],
    "source": null,
    "source_url": "https://example.com/jobs/ai-operations-lead",
    "external_id": null,
    "imported_at": "<timestamp>"
  },
  "duplicate": false,
  "match": {
    "id": "<match-id>"
  }
}
```

Safety controls:

- Allows only `http` and `https`.
- Rejects localhost/private/local network URLs.
- Rejects credentialed URLs.
- Uses timeout.
- Limits response size.
- Converts HTML to readable text.
- Does not use browser automation, cookies, sessions, paid APIs, or LinkedIn
  scraping.

### Ad Hoc Match From Request Body

Status: active

Endpoint:

```text
POST /match
```

Authentication:

- Not required.

Request format:

```json
{
  "candidate": {
    "name": "Demo Candidate",
    "headline": "AI Operations Candidate",
    "location": "Remote",
    "summary": "Short candidate summary.",
    "target_roles": ["AI Operations Lead"],
    "skills": ["Python", "SQL"],
    "experience_highlights": ["Built reporting workflows."],
    "portfolio_links": []
  },
  "job": {
    "title": "AI Operations Lead",
    "company": "ExampleTech",
    "location": "Remote",
    "description": "Lead automation and reporting.",
    "required_skills": ["Python", "SQL"],
    "nice_to_have_skills": []
  }
}
```

Response format:

Deterministic match result, including score, strengths, gaps, recommendations,
and explanation fields.

Notes:

- This endpoint can generate a match from real structured input in one request.
- It does not persist the candidate, job, or match.
- It does not parse CV or job documents.

### Persisted Match From Existing Candidate And Job

Status: active

Endpoint:

```text
POST /matches/persist
```

Authentication:

- Required.

Request format:

```json
{
  "candidate_profile_id": "<candidate-id>",
  "job_description_id": "<job-id>"
}
```

Response format:

Persisted `match_results` database row.

Notes:

- Candidate ownership is enforced.
- Job lookup is by job ID.
- This is the main persisted matching endpoint when candidate/job already exist.

## Specific Intake Questions

| Question | Current Answer | Evidence |
| --- | --- | --- |
| Can a user upload CV PDF? | No | No multipart upload, PDF parser, file storage, or `/cv`/`/resume` upload endpoint found. |
| Can a user upload DOCX? | No | No DOCX parser or upload endpoint found. |
| Can a user paste CV text? | No, not as raw CV text parsing | `POST /candidates` accepts structured profile JSON only. |
| Can a user paste structured candidate profile data? | Yes | `POST /candidates` accepts `CandidateProfile` JSON. |
| Can a user paste job description? | Yes | `POST /jobs/import-text` accepts `raw_text`. |
| Can a user import job URL? | Yes | `POST /jobs/import-url` fetches and imports safe public HTTP(S) URLs. |
| Can a user generate match from real input? | Yes, if input is structured | `POST /match`, `POST /matches/persist`, and optional `match_candidate_id` on job import support matching. |
| Can a user generate match from uploaded CV file? | No | Missing CV file upload and parsing. |

## Sprint 13 UI Comparison

### Exposed In Sprint 13 UI

Sprint 13 frontend includes API client methods for:

- `POST /candidates`
- `GET /candidates`
- `POST /jobs/import-text`
- `POST /matches/persist`
- `POST /applications/package`
- `POST /applications`
- `POST /outcomes`
- reporting and insights endpoints

The guided beta workflow can:

- create a candidate
- import a job from hardcoded text
- review/create a match
- generate a package
- create an application
- move through pipeline
- record outcome
- view insights

### Present In Backend But Not Fully Exposed In UI

| Backend capability | UI exposure status | Gap |
| --- | --- | --- |
| Structured candidate profile creation | Partially exposed | Guided workflow uses prefilled demo candidate values; no user-editable candidate intake form. |
| Candidate listing | Not meaningfully exposed | Profile view does not provide full candidate selection/intake management. |
| Pasted job text import | Partially exposed | Guided workflow uses hardcoded job text; no user-facing paste textarea in the dashboard flow. |
| Job URL import | Not exposed | Frontend API does not call `/jobs/import-url`; no URL input exists. |
| Optional match during job import | Partially exposed | Frontend passes candidate ID for text import, but only through guided demo flow. |
| Direct structured job creation | Not exposed | No structured job form. |
| Persisted match from existing candidate/job | Partially exposed | Used by guided flow, not exposed as a general user action. |
| Ad hoc `/match` endpoint | Not exposed | No UI form for structured candidate/job match preview without persistence. |

### Missing In Both Backend And UI

| Capability | Status |
| --- | --- |
| CV PDF upload | Missing |
| DOCX upload | Missing |
| Resume/CV parsing | Missing |
| Pasted CV text parser | Missing |
| Candidate import from raw CV text | Missing |
| LinkedIn profile export import | Intentionally absent by guardrail |

## Recommendation

### Option A: Reuse Existing Backend Capabilities

Use existing backend capabilities for the next UI intake increment:

- Build a real candidate profile form around `POST /candidates`.
- Build a candidate list/selector around `GET /candidates`.
- Build a job paste textarea around `POST /jobs/import-text`.
- Build a job URL input around `POST /jobs/import-url`.
- Let users choose whether to pass `match_candidate_id` during job import.
- Reuse `POST /matches/persist` for matching existing candidate/job records.

This option is appropriate for:

- job description paste intake
- job URL intake
- structured candidate profile intake
- deterministic matching from already structured data

### Option B: Missing Capabilities Must Be Built

Build new backend capabilities if the product needs CV/resume intake:

- `POST /candidates/import-text` for pasted CV/resume text.
- Optional deterministic parser that extracts name, headline, location, skills,
  target roles, and experience highlights into `CandidateProfile`.
- Later, a controlled `POST /candidates/import-file` if PDF/DOCX upload becomes
  a requirement.

File upload should remain out of scope until security/storage decisions are made:

- supported file types
- size limits
- malware scanning
- temporary storage policy
- PII retention policy
- parser dependencies
- deletion/export workflows

## Final Decision

Use Option A immediately for UI exposure of existing backend capabilities.

Use Option B only for CV/resume parsing and file upload, because those
capabilities do not currently exist.

The most practical next product step is a real Intake UI layer:

1. Candidate profile form using `POST /candidates`.
2. Job paste form using `POST /jobs/import-text`.
3. Job URL form using `POST /jobs/import-url`.
4. Candidate/job selector for `POST /matches/persist`.
5. Keep CV PDF/DOCX upload out of scope until a dedicated secure intake sprint.
