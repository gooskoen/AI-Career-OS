# AI-Career-OS

An open-source AI-powered job hunting and career intelligence system.

This repository currently contains a simple MVP foundation with mock/demo data only.
Do not commit private CVs, LinkedIn exports, personal data, API keys, or real contacts.

## MVP Scope

- FastAPI backend
- PostgreSQL schema for candidate profiles, jobs, match results, and interview briefings
- Example candidate profile JSON with demo data
- ATS/job matching engine
- Interview briefing generator
- Docker Compose setup for API and database

## Architecture

```text
AI-Career-OS
+-- backend/
|   +-- app/
|   |   +-- main.py        # FastAPI routes
|   |   +-- matching.py    # ATS-style keyword matching
|   |   +-- briefing.py    # Interview briefing generator
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
