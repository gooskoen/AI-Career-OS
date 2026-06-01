# Reporting & Insights

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Purpose

Sprint 12 adds a read-only reporting layer over existing Applications, Outcomes,
Pipeline statuses, and user ownership. It helps a candidate understand pipeline
health, funnel conversion, skill performance, and recommendation usage without adding
CRM, automation, AI, or frontend dashboard scope.

## Ownership

All reporting endpoints require a bearer token and only read records owned by the
authenticated user. Reporting queries are scoped by `user_id` in the repository layer.

```bash
curl "http://localhost:8000/reporting/dashboard?time_window=all_time" \
  -H "Authorization: Bearer <access-token>"
```

## Time Windows

Every reporting endpoint supports:

- `last_30_days`
- `last_90_days`
- `last_year`
- `all_time`

The filter is applied to application and outcome `created_at` timestamps.

## Dashboard

```bash
curl "http://localhost:8000/reporting/dashboard?time_window=last_90_days" \
  -H "Authorization: Bearer <access-token>"
```

Sample response:

```json
{
  "active_applications": 4,
  "interviews_scheduled": 1,
  "offers_received": 1,
  "hires": 0,
  "rejections": 2,
  "pipeline_totals": {
    "drafted": 1,
    "applied": 2,
    "recruiter_replied": 1,
    "interview_scheduled": 1,
    "interview_completed": 0,
    "offer_received": 1,
    "hired": 0,
    "rejected": 2,
    "withdrawn": 0
  }
}
```

## Funnel

```bash
curl "http://localhost:8000/reporting/funnel?time_window=all_time" \
  -H "Authorization: Bearer <access-token>"
```

Sample response:

```json
{
  "applications": 10,
  "recruiter_replies": 4,
  "interviews": 3,
  "offers": 1,
  "hires": 1,
  "application_to_reply_rate": 0.4,
  "reply_to_interview_rate": 0.75,
  "interview_to_offer_rate": 0.33,
  "offer_to_hire_rate": 1.0
}
```

## Application Analytics

```bash
curl "http://localhost:8000/reporting/applications?time_window=last_year" \
  -H "Authorization: Bearer <access-token>"
```

Returns:

- `applications_by_status`
- `applications_by_source`
- `applications_by_month`
- `applications_by_job_family`

## Outcome Analytics

```bash
curl "http://localhost:8000/reporting/outcomes?time_window=all_time" \
  -H "Authorization: Bearer <access-token>"
```

Returns rejection, offer, and hire rates plus monthly outcome trends.

## Skill Analytics

```bash
curl "http://localhost:8000/reporting/skills?time_window=all_time" \
  -H "Authorization: Bearer <access-token>"
```

Returns:

- `strongest_performing_skills`
- `weakest_performing_skills`
- `most_successful_skills`
- `rejection_linked_skills`

Skill performance is derived from outcome history and the deterministic skill metadata
already captured with outcomes.

## Recommendation Analytics

```bash
curl "http://localhost:8000/reporting/recommendations?time_window=all_time" \
  -H "Authorization: Bearer <access-token>"
```

Returns followed/ignored counts and usage rates for:

- CV edits applied
- cover letter used
- interview prep used

## Candidate Insights V2

`GET /insights/candidate/{candidate_id}` now includes:

- `top_job_families`
- `recurring_rejection_patterns`
- `strongest_skill_clusters`
- `focus_recommendations`

The endpoint remains deterministic and user-scoped.

## Guardrails

Sprint 12 does not add:

- recruiter CRM
- email sending
- automation
- AI or LLM calls
- web browsing
- LinkedIn automation
- dashboard frontend
