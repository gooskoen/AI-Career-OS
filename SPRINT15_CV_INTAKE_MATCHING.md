# Sprint 15 Proposal: CV Intake And Matching Quality

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Goal

Add CV-driven intake and improve deterministic matching quality so V1 can be
validated against realistic CV and vacancy examples.

## Product Context

Sprint 14 made the system usable through a guided intake wizard, but the V1 product
direction is now clearer:

AI-Career-OS is primarily a CV-driven matching and application preparation tool.

Manual candidate entry remains a useful fallback, but Sprint 15 should make pasted
CV text the main intake path.

## Scope

### A. CV Text Import

Add a frontend field:

- Paste CV text

Do not add PDF or DOCX upload in this sprint unless it is already trivial and
reliable. Avoid fragile document parsing.

### B. CV Skill Extraction

Extract:

- skills
- roles
- experience highlights
- certifications
- domains
- seniority indicators

Keep extraction deterministic first. Use simple keyword, section, and pattern
rules before introducing external AI or LLM dependencies.

### C. Vacancy Requirement Extraction

Extract:

- required skills
- preferred skills
- responsibilities
- domain keywords
- seniority indicators

Reuse the existing job ingestion layer where possible, but improve the extracted
structure enough to support realistic matching.

### D. Match Algorithm Improvement

Calculate:

- hard skill match
- domain match
- seniority match
- role alignment
- certification/framework match

Return:

- overall match percentage
- weighted sub-scores
- strengths
- gaps
- recommended CV changes

The score must remain deterministic and explainable.

### E. CV Update Suggestions

Generate deterministic suggestions:

- summary update
- skills section update
- experience bullet suggestions
- keyword alignment
- missing evidence warnings

Suggestions should be actionable. Prefer:

```text
Add a BPMN modelling bullet under your workflow automation experience.
```

over:

```text
Improve BPMN experience.
```

### F. Cover Letter Generation

Generate a deterministic first draft using:

- candidate profile
- vacancy
- strengths
- gaps
- professional tone

No external LLM is required for this sprint.

### G. Application Creation

Store or link:

- candidate
- job
- match
- CV suggestions
- cover letter
- application status

Application remains the central aggregate for tracking the pipeline.

## Test Data

Add realistic fixtures:

- sample CV text
- sample vacancy text
- expected extracted skills
- expected extracted roles/domains
- expected match bands
- expected CV recommendation themes

Fixtures must be mock/demo data only. Do not include private CVs, LinkedIn exports,
real recruiter contacts, or personal data.

## Tests

Add tests for:

- CV text import
- skill extraction
- vacancy extraction
- scoring
- gap detection
- CV update suggestions
- cover letter generation
- application creation

## Acceptance Criteria

User can:

1. Paste CV.
2. Paste vacancy.
3. Generate match.
4. See score.
5. See extracted skills.
6. See gaps.
7. See CV update suggestions.
8. Generate cover letter.
9. Create application.
10. Track in pipeline.

## Guardrails

Do not add:

- recruiter CRM
- email sending
- LinkedIn automation
- application automation
- paid APIs
- external LLM dependency
- broad resume parser scope unless explicitly approved

## Recommended Delivery Order

1. Define CV text request/response models.
2. Add deterministic CV extraction helpers.
3. Improve vacancy extraction helpers.
4. Add weighted sub-score model.
5. Add CV recommendation generator.
6. Add deterministic cover letter generator updates.
7. Wire frontend wizard to CV text first.
8. Add realistic fixtures and tests.
