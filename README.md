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

```text
AI-Career-OS
+-- backend/
|   +-- app/
|   |   +-- main.py        # FastAPI routes
|   |   +-- matching.py    # ATS-style keyword matching
|   |   +-- briefing.py    # Interview briefing generator
|   |   +-- database.py    # PostgreSQL connection helper
|   |   +-- ingestion.py   # Job text and URL import helpers
|   |   +-- repositories.py # Data-access functions
|   |   +-- schemas.py     # Pydantic request/response models
|   +-- Dockerfile
|   +-- requirements.txt
+-- database/
|   +-- schema.sql         # PostgreSQL schema
+-- examples/
|   +-- candidate_profile.example.json
+-- docker-compose.yml
```

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
- `GET /demo/candidate`
- `GET /demo/match`
- `POST /match`
- `POST /briefing`
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
score, a score breakdown, strengths, gaps, and recommended actions.

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
