# AI-Career-OS

[![CI](https://github.com/gooskoen/AI-Career-OS/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/gooskoen/AI-Career-OS/actions/workflows/ci.yml)

An open-source AI-powered job hunting and career intelligence system.

This repository currently contains a simple MVP foundation with mock/demo data only.
Do not commit private CVs, LinkedIn exports, personal data, API keys, or real contacts.

Sprint 3 adds a simple job ingestion layer for importing job vacancies from raw text
or safe public URLs into PostgreSQL.

## MVP Scope

- FastAPI backend
- PostgreSQL schema for candidate profiles, jobs, match results, and interview briefings
- Example candidate profile JSON with demo data
- ATS/job matching engine
- Interview briefing generator
- Docker Compose setup for API and database
- PostgreSQL persistence endpoints for Sprint 2
- Job ingestion endpoints for Sprint 3
- Deterministic matching and gap analysis for Sprint 4
- Deterministic application package generation for Sprint 5
- Deterministic company and recruiter intelligence for Sprint 6
- Deterministic feedback and outcome analytics for Sprint 7
- First-class Application domain model for Sprint 8
- Architecture hardening, migrations, router/repository boundaries, standard errors,
  status events, and application pagination for Sprint 9
- Application pipeline and Kanban-ready workflow endpoints for Sprint 10
- Authentication and user ownership foundation for Sprint 11

## Persistence Status

The PostgreSQL schema in `database/schema.sql` defines the planned data model for
candidate profiles, job descriptions, match results, and interview briefings.

Sprint 2 adds MVP PostgreSQL persistence through small repository functions using
`psycopg`. The API stores structured candidate profiles, job descriptions, match
results, and interview briefings. It does not store private CV files, LinkedIn exports,
recruiter contacts, API keys, or other secret/private source files.

The Sprint 3 ingestion layer is not a crawler and does not bypass website terms,
authentication, robots controls, paywalls, or session-based access. It only supports
simple HTTP GET requests against safe public `http` and `https` URLs.

## Architecture

See [`docs/architecture.md`](docs/architecture.md) for the current architecture
notes, router/repository layout, response model direction, status event model, and
user ownership model.

```text
AI-Career-OS
+-- backend/
|   +-- app/
|   |   +-- main.py        # FastAPI app wiring
|   |   +-- auth.py        # Password hashing and JWT helpers
|   |   +-- routers/       # Route groups by domain
|   |   +-- repositories/  # Data-access functions by aggregate
|   |   +-- matching.py    # ATS-style keyword matching
|   |   +-- application_package.py # Template-based application materials
|   |   +-- company_intelligence.py # Company and recruiter preparation
|   |   +-- application_domain.py # Application status and notes models
|   |   +-- feedback.py    # Outcome analytics and candidate insights
|   |   +-- briefing.py    # Interview briefing generator
|   |   +-- database.py    # PostgreSQL connection helper
|   |   +-- ingestion.py   # Job text and URL import helpers
|   |   +-- schemas.py     # Pydantic request/response models
|   +-- Dockerfile
|   +-- requirements.txt
+-- database/
|   +-- schema.sql         # PostgreSQL schema
+-- docs/
|   +-- api.md
|   +-- architecture.md
|   +-- migrations.md
+-- migrations/
|   +-- versions/
+-- examples/
|   +-- candidate_profile.example.json
+-- docker-compose.yml
```

Additional docs:

- [`docs/api.md`](docs/api.md)
- [`docs/authentication.md`](docs/authentication.md)
- [`docs/migrations.md`](docs/migrations.md)
- [`docs/security.md`](docs/security.md)

## Quick Start

Run the full stack:

```bash
docker compose up --build
```

Optional local environment setup:

```bash
cp .env.example .env
```

Open the API docs:

```text
http://localhost:8000/docs
```

Useful endpoints:

- `GET /health`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `GET /demo/candidate`
- `GET /demo/match`
- `POST /match`
- `POST /briefing`
- `POST /applications/package`
- `POST /applications`
- `GET /applications`
- `GET /applications/{application_id}`
- `PATCH /applications/{application_id}/status`
- `POST /applications/{application_id}/notes`
- `POST /intelligence/company`
- `POST /outcomes`
- `GET /outcomes/{candidate_id}`
- `GET /insights/candidate/{candidate_id}`
- `POST /candidates`
- `GET /candidates`
- `POST /jobs`
- `GET /jobs`
- `POST /jobs/import-text`
- `POST /jobs/import-url`
- `POST /matches/persist`
- `GET /matches`
- `POST /briefings/persist`
- `GET /briefings`

Sprint 11 protects private persistence and workflow endpoints with bearer token
authentication. Register or log in first, then send:

```bash
Authorization: Bearer <access-token>
```

## Sprint 2 Persistence Usage

Start the stack with PostgreSQL:

```bash
cp .env.example .env
docker compose up --build
```

Create a candidate profile:

```bash
curl -X POST http://localhost:8000/candidates \
  -H "Content-Type: application/json" \
  -d @examples/candidate_profile.example.json
```

Create a job description:

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Product Operations Lead",
    "company": "ExampleTech",
    "description": "Lead AI product operations and workflow automation.",
    "required_skills": ["AI strategy", "workflow automation"],
    "nice_to_have_skills": ["FastAPI", "PostgreSQL"]
  }'
```

Persisted matches and briefings are created from stored record IDs:

```bash
curl -X POST http://localhost:8000/matches/persist \
  -H "Content-Type: application/json" \
  -d '{"candidate_profile_id":"<candidate-id>","job_description_id":"<job-id>"}'

curl -X POST http://localhost:8000/briefings/persist \
  -H "Content-Type: application/json" \
  -d '{"match_result_id":"<match-id>"}'
```

## Sprint 3 Job Ingestion Usage

### LinkedIn Manual Import

LinkedIn support in Sprint 3 is manual import only. Copy the visible job text from
LinkedIn and paste it into `POST /jobs/import-text`; optionally include the public
LinkedIn job URL as `source_url` so the import stores `source = "linkedin"` and an
`external_id` when one can be extracted from the URL.

```bash
curl -X POST http://localhost:8000/jobs/import-text \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Senior AI Product Manager\nExampleTech\nBrussels, Belgium (Hybrid)\nAbout the job\nLead AI roadmap delivery, workflow automation, analytics, Python, SQL, and stakeholder management.",
    "source_url": "https://www.linkedin.com/jobs/view/4242424242/",
    "match_candidate_id": "<candidate-id>"
  }'
```

This endpoint stores the imported job, returns `duplicate: true` when the job already
exists by `source_url` or by company/title/location, and optionally returns a persisted
match result when `match_candidate_id` is supplied.

Import a job from raw text:

```bash
curl -X POST http://localhost:8000/jobs/import-text \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "AI Product Operations Lead\nLead workflow automation, analytics, SQL, Python, and stakeholder management.",
    "source_url": "https://example.com/jobs/ai-product-operations-lead"
  }'
```

Import a job from raw text and immediately match it against an existing candidate:

```bash
curl -X POST http://localhost:8000/jobs/import-text \
  -H "Content-Type: application/json" \
  -d '{
    "raw_text": "Automation Program Manager\nOwn workflow automation, analytics, and responsible AI delivery.",
    "match_candidate_id": "<candidate-id>"
  }'
```

Import a job from a safe public URL:

```bash
curl -X POST http://localhost:8000/jobs/import-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/jobs/ai-product-operations-lead",
    "match_candidate_id": "<candidate-id>"
  }'
```

URL imports reject non-HTTP schemes, localhost/private network targets, credentialed
URLs, oversized responses, and fetches that exceed the configured timeout. Do not use
this layer for LinkedIn automation, credential-based scraping, cookies, session tokens,
or paid scraping APIs.

## Sprint 4 Matching And Gap Analysis

Sprint 4 keeps matching deterministic. The `POST /match` endpoint returns an overall
score, weighted score breakdown, matched and missing skills, ranked strengths,
critical/moderate/optional gaps, recommended actions, and a reasoning summary.

```bash
curl -X POST http://localhost:8000/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Alex Demo",
      "headline": "Automation specialist",
      "location": "Remote",
      "summary": "Builds analytics and workflow automation systems.",
      "target_roles": ["AI Product Operations Lead"],
      "skills": ["Python", "SQL", "workflow automation", "analytics"],
      "experience_highlights": ["Delivered Python and SQL analytics for operations teams."]
    },
    "job": {
      "title": "AI Product Operations Lead",
      "company": "ExampleTech",
      "description": "Lead Python, SQL, workflow automation, Kubernetes, and GraphQL work.",
      "required_skills": ["Python", "SQL", "Kubernetes"],
      "nice_to_have_skills": ["GraphQL", "workflow automation"]
    }
  }'
```

No paid APIs, scraping, LinkedIn automation, or application sending are part of Sprint 4.

## Sprint 5 Application Package Usage

Sprint 5 generates deterministic, template-based application materials from a
candidate profile, job description, and existing match result. It does not call LLMs,
send email, automate LinkedIn, or apply to jobs.

```bash
curl -X POST http://localhost:8000/applications/package \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Alex Demo",
      "headline": "Automation specialist",
      "location": "Remote",
      "summary": "Builds analytics and workflow automation systems with 6 years of experience.",
      "target_roles": ["AI Product Operations Lead"],
      "skills": ["Python", "SQL", "Kubernetes", "workflow automation"],
      "experience_highlights": ["Delivered Python analytics for operations teams."]
    },
    "job": {
      "title": "AI Product Operations Lead",
      "company": "ExampleTech",
      "description": "Lead Python, SQL, workflow automation, and Kubernetes delivery.",
      "required_skills": ["Python", "SQL", "Kubernetes"],
      "nice_to_have_skills": ["GraphQL", "workflow automation"]
    },
    "match_result": {
      "score": 82,
      "score_breakdown": {"overall": 82, "keyword": 70, "required": 100, "nice_to_have": 50},
      "matched_keywords": ["python", "sql"],
      "missing_keywords": ["graphql"],
      "matched_skills": ["Python", "SQL", "Kubernetes"],
      "missing_skills": ["GraphQL"],
      "strengths": [{"skill": "Python", "contribution": 60, "reason": "Matches a required skill.", "evidence": ["Delivered Python analytics for operations teams."]}],
      "gaps": {"critical": [], "moderate": [], "optional": ["GraphQL"]},
      "recommended_actions": ["Add a concise side project or learning note for GraphQL."],
      "explanation": null,
      "candidate_highlights": ["Delivered Python analytics for operations teams."],
      "recommendation": "Strong match: tailor the application around the shared keywords."
    }
  }'
```

The response includes `tailored_summary`, `cover_letter`, `talking_points`,
`key_strengths`, `risk_gaps`, and `recommended_cv_edits`.

## Sprint 6 Company Intelligence Usage

Sprint 6 generates deterministic company and recruiter preparation from the job,
candidate, match result, application package, and optional notes supplied by the user.
It does not browse the web, call paid APIs, scrape sites, automate LinkedIn, send email,
or contact recruiters.

```bash
curl -X POST http://localhost:8000/intelligence/company \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "title": "AI Product Operations Lead",
      "company": "ExampleTech",
      "description": "Lead Python, SQL, workflow automation, and Kubernetes delivery for internal teams.",
      "required_skills": ["Python", "SQL", "Kubernetes"],
      "nice_to_have_skills": ["GraphQL", "workflow automation"]
    },
    "candidate": {
      "name": "Alex Demo",
      "headline": "Automation specialist",
      "location": "Remote",
      "summary": "Builds analytics and workflow automation systems with 6 years of experience.",
      "target_roles": ["AI Product Operations Lead"],
      "skills": ["Python", "SQL", "Kubernetes", "workflow automation"],
      "experience_highlights": ["Delivered Python analytics for operations teams."]
    },
    "match_result": {
      "score": 82,
      "score_breakdown": {"overall": 82, "keyword": 70, "required": 100, "nice_to_have": 50},
      "matched_keywords": ["python", "sql"],
      "missing_keywords": ["graphql"],
      "matched_skills": ["Python", "SQL", "Kubernetes"],
      "missing_skills": ["GraphQL"],
      "strengths": [{"skill": "Python", "contribution": 60, "reason": "Matches a required skill.", "evidence": ["Delivered Python analytics for operations teams."]}],
      "gaps": {"critical": [], "moderate": [], "optional": ["GraphQL"]},
      "recommended_actions": ["Add a concise side project or learning note for GraphQL."],
      "explanation": null,
      "candidate_highlights": ["Delivered Python analytics for operations teams."],
      "recommendation": "Strong match: tailor the application around the shared keywords."
    },
    "application_package": {
      "tailored_summary": "Alex Demo is positioned for the role through Python.",
      "cover_letter": "Dear ExampleTech hiring team, I am interested in the role.",
      "talking_points": ["Connect prior work to Python."],
      "key_strengths": ["Python", "SQL"],
      "risk_gaps": ["GraphQL"],
      "recommended_cv_edits": ["Add a CV bullet with measurable evidence for Python."]
    },
    "company_notes": "Manual note: internal automation team.",
    "recruiter_notes": "Manual note: recruiter prefers concise context."
  }'
```

The response includes `company_summary`, `likely_business_needs`,
`interview_focus_areas`, `questions_to_ask`, `recruiter_message_draft`,
`salary_positioning_notes`, `risk_flags`, and `next_best_actions`.

## Sprint 7 Feedback Learning Loop Usage

Sprint 7 captures application outcomes and computes deterministic conversion metrics
and candidate insights. It does not use machine learning, LLMs, web browsing, LinkedIn
automation, or automatic applications.

Create an outcome:

```bash
curl -X POST http://localhost:8000/outcomes \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "<candidate-id>",
    "job_id": "<job-id>",
    "application_id": "<application-id>",
    "outcome": "recruiter_replied",
    "notes": "Recruiter replied after tailored CV update.",
    "cv_edits_applied": true,
    "cover_letter_used": true,
    "interview_prep_used": false,
    "skills": ["Python", "workflow automation"],
    "job_family": "AI Operations"
  }'
```

Fetch outcome history and conversion metrics:

```bash
curl http://localhost:8000/outcomes/<candidate-id>
```

Fetch deterministic candidate insights:

```bash
curl http://localhost:8000/insights/candidate/<candidate-id>
```

Supported outcomes are `applied`, `recruiter_replied`, `interview_scheduled`,
`interview_completed`, `rejected`, `offer_received`, `hired`, and `withdrawn`.
The analytics include application-to-reply, reply-to-interview, interview-to-offer,
and offer-to-hire rates.

## Sprint 8 Application Domain Model

Sprint 8 introduces `Application` as the primary business object connecting candidates,
jobs, matches, generated packages, company intelligence, outcomes, and notes.

```text
Candidate
    |
    v
Application
    |
    v
Job

Application
+-- MatchResult
+-- ApplicationPackage
+-- CompanyIntelligence
+-- Outcomes
+-- Notes
```

Create an application:

```bash
curl -X POST http://localhost:8000/applications \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "<candidate-id>",
    "job_id": "<job-id>",
    "status": "drafted",
    "source": "manual",
    "match_result_id": "<match-result-id>"
  }'
```

List and retrieve applications:

```bash
curl "http://localhost:8000/applications?status=drafted&page=1&page_size=25"
curl http://localhost:8000/applications/<application-id>
```

`GET /applications` supports `status`, `candidate_id`, `job_id`, `page`, and
`page_size`. The response uses a paginated envelope with `success`, `data`, `page`,
`page_size`, and `total`.

Update application status:

```bash
curl -X PATCH http://localhost:8000/applications/<application-id>/status \
  -H "Content-Type: application/json" \
  -d '{"status": "interview_scheduled"}'
```

Add an application note:

```bash
curl -X POST http://localhost:8000/applications/<application-id>/notes \
  -H "Content-Type: application/json" \
  -d '{"note": "Prepare a stronger Kubernetes project example before interview."}'
```

Fetch application status history:

```bash
curl http://localhost:8000/applications/<application-id>/status-events
```

Sprint 8 remains deterministic domain modeling only. It does not add dashboards,
machine learning, LLM integration, web browsing, LinkedIn automation, or automatic
applications.

## Sprint 9 Architecture Hardening

Sprint 9 adds Alembic migrations, domain routers, repository modules, standard error
responses, validation hardening, application status events, and pagination/filtering
for applications. It does not add dashboards, kanban, reporting, recruiter CRM,
authentication, LLM integration, web browsing, LinkedIn automation, or automatic
applications.

Migration commands:

```bash
alembic heads
alembic upgrade head
```

## Sprint 11 Authentication And Ownership

Sprint 11 adds local JWT authentication and user ownership for private career data.
Candidate profiles, applications, notes, outcomes, persisted matches, and persisted
briefings are scoped by `user_id` in repository queries.

See [`docs/authentication.md`](docs/authentication.md) and
[`docs/security.md`](docs/security.md) for the token flow and authorization rules.

Sprint 11 does not add OAuth, social login, reporting, recruiter CRM, LLM integration,
web browsing, email sending, LinkedIn automation, or automatic applications.

## Local Backend Development

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Data Safety

Only mock data belongs in this repository. Keep private career material outside git,
including CVs, resumes, LinkedIn exports, recruiter contacts, personal notes, API keys,
and any real candidate or employer records.

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
