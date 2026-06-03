# Product Scope V1

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Product Definition

AI-Career-OS V1 is a CV-driven job matching and application preparation system.

The core user value is not generic candidate data entry. The core value is helping a
candidate turn a real CV and a real vacancy into:

- an extracted candidate profile
- extracted skills and experience signals
- extracted job requirements
- an accurate match percentage
- strengths and gaps
- recommended CV updates
- a cover letter draft
- an application record
- pipeline tracking

## V1 Workflow

V1 must support this workflow:

1. Import CV.
2. Extract candidate profile and skills.
3. Import vacancy.
4. Extract job requirements and skills.
5. Calculate accurate match percentage.
6. Explain strengths and gaps.
7. Suggest CV updates.
8. Generate cover letter.
9. Create application.
10. Track pipeline.

## Core Capabilities

### CV Intake

V1 must allow a user to provide CV content. The first production-ready version can
start with pasted CV text. PDF and DOCX upload are valuable, but they are not
required unless implementation is straightforward and reliable.

### Candidate Extraction

The system should extract, at minimum:

- skills
- roles
- experience highlights
- certifications
- domains
- seniority indicators

### Vacancy Extraction

The system should extract, at minimum:

- required skills
- preferred skills
- responsibilities
- domain keywords
- seniority indicators

### Matching

The match score must be explainable and deterministic for V1. It should consider:

- hard skill match
- domain match
- seniority match
- role alignment
- certification and framework match

The output must include:

- overall match percentage
- weighted sub-scores
- strengths
- gaps
- recommended CV changes

### Application Preparation

The system should generate deterministic first drafts for:

- CV update suggestions
- cover letter
- application package content

These should use the extracted CV profile, vacancy requirements, match strengths,
and known gaps.

## Supporting Capabilities

Manual candidate entry is supportive, not core. It remains useful for demos,
corrections, and fallback workflows, but V1 readiness should be judged against
CV-driven intake and matching.

The existing application pipeline remains part of V1 because it lets users track
real applications after matching and preparation.

## Explicitly V2 Or Later

Recruiter CRM is V2.

The following are not required for V1:

- recruiter CRM
- contact enrichment
- outreach sequencing
- email sending
- LinkedIn automation
- application automation
- broad public SaaS hardening

## V1 Readiness Rule

AI-Career-OS should not be called V1-ready until realistic CV and vacancy examples
can be used to validate extraction, match quality, CV update recommendations, cover
letter generation, application creation, and pipeline tracking.
