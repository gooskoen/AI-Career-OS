# AI-Career-OS

[![CI](https://github.com/gooskoen/AI-Career-OS/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/gooskoen/AI-Career-OS/actions/workflows/ci.yml)

An open-source AI-powered job hunting and career intelligence system.

This repository currently contains a simple MVP foundation with mock/demo data only.
Do not commit private CVs, LinkedIn exports, personal data, API keys, or real contacts.

Sprint 2 adds PostgreSQL persistence for structured MVP records. The demo endpoints
still operate on checked-in mock data only.

## MVP Scope

- FastAPI backend
- PostgreSQL schema for candidate profiles, jobs, match results, and interview briefings
- Example candidate profile JSON with demo data
- ATS/job matching engine
- Interview briefing generator
- Docker Compose setup for API and database
- PostgreSQL persistence endpoints for Sprint 2

## Persistence Status

The PostgreSQL schema in `database/schema.sql` defines the planned data model for
candidate profiles, job descriptions, match results, and interview briefings.

Sprint 2 adds MVP PostgreSQL persistence through small repository functions using
`psycopg`. The API stores structured candidate profiles, job descriptions, match
results, and interview briefings. It does not store private CV files, LinkedIn exports,
recruiter contacts, API keys, or other secret/private source files.

## Architecture

```text
AI-Career-OS
+-- backend/
|   +-- app/
|   |   +-- main.py        # FastAPI routes
|   |   +-- matching.py    # ATS-style keyword matching
|   |   +-- briefing.py    # Interview briefing generator
|   |   +-- database.py    # PostgreSQL connection helper
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
