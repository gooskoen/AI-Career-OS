# Sprint 16 Proposal: Application Experience

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Goal

Transform the application board from a technical tracking screen into a career
decision cockpit.

Sprint 16 should help a user understand, at a glance:

- what job each application is for
- which company it belongs to
- how strong the match is
- what action is needed next
- where the candidate is strong
- where the candidate has gaps
- which applications need attention

## Product Context

AI-Career-OS V1 is now framed around CV-driven matching and application
preparation. The core workflow is functional, but the Application and Kanban
experience still exposes technical identifiers and implementation details instead
of decision-making information.

Sprint 16 should focus on presenting existing data better. It should not change
matching, CV extraction, cover letter generation, or backend architecture.

## Scope

### 1. Kanban Card Redesign

Replace technical card content such as source and UUID with useful business
information.

Primary card content:

- Job Title
- Company Name

Secondary card content:

- Match Percentage
- Candidate Name

Metadata:

- Application Date
- Last Activity
- Days in Stage

Cards should answer the user's first question without requiring a click:

```text
What application is this?
```

### 2. Match Visibility

Display match percentage directly on each application card.

Use a simple color indicator:

- Green: 80%+
- Yellow: 60-79%
- Red: below 60%

This is a display rule only. Do not change scoring or matching logic.

### 3. Next Action Visibility

Display the next action directly on the card.

Examples:

- Follow up tomorrow
- Waiting recruiter response
- Prepare interview
- Review offer

The board should make applications requiring attention obvious without requiring
the user to open every detail page.

### 4. Application Detail Redesign

Replace technical identifiers with readable labels.

Display:

```text
Candidate: <Name>
Job: <Title>
Company: <Name>
Match: <Score>
Status: <Current Status>
Next Action: <Action>
Days in Stage: <Value>
```

UUIDs should be hidden from the normal user interface unless a debug view is
explicitly introduced later.

### 5. Strengths And Gaps

Use existing match data to display:

Top Strengths:

- Skill 1
- Skill 2
- Skill 3

Top Gaps:

- Skill A
- Skill B
- Skill C

Do not create a new matching engine. Do not change the matching model. This
scope is presentation and prioritization only.

### 6. Timeline View

Show a readable application timeline:

- Drafted
- Applied
- Recruiter Replied
- Interview
- Offer
- Hired

Include timestamps where available.

Use existing application status events. Do not add new application states.

### 7. Candidate Context

Every application card and detail view must clearly show the candidate name.

The user should never need to recognize an application by UUID.

### 8. Dashboard Improvements

Improve the dashboard with decision-oriented sections:

- Top Matches
- Recent Applications
- Applications Requiring Action
- Upcoming Follow-ups

Use existing reporting, application summary, board, next action, and readiness
data where available.

## UX Tests

Add tests verifying:

- Kanban cards show meaningful business information.
- UUIDs are hidden unless debugging.
- Match score is visible.
- Match color indicator follows the existing score value.
- Company name is visible.
- Job title is visible.
- Candidate name is visible.
- Next action is visible.
- Application detail uses readable labels.
- Timeline renders existing status events.
- Dashboard highlights applications requiring action.

## Documentation

Create:

```text
docs/application-experience.md
```

Document:

- card layout
- detail layout
- match visualization
- action tracking
- timeline display
- dashboard decision sections

## Acceptance Criteria

User can answer instantly:

- What job is this?
- For which company?
- How well do I match?
- What is my next action?
- What are my biggest gaps?
- Which applications need attention?

The user should not need to open technical details or inspect UUIDs to answer
these questions.

## Guardrails

Do not add:

- recruiter CRM
- AI additions
- backend redesign
- new matching logic
- new CV extraction logic
- new cover letter generation logic
- new application states
- email sending
- LinkedIn automation
- application automation

Use existing backend data.

## Recommended Delivery Order

1. Audit current board and application summary data available to the frontend.
2. Define card view model derived from existing API responses.
3. Redesign Kanban cards.
4. Redesign application detail labels and sections.
5. Add strengths/gaps display from existing match data.
6. Add timeline rendering from existing status events.
7. Add dashboard decision sections.
8. Add UX tests.
9. Add `docs/application-experience.md`.

## Non-Goals

Sprint 16 is not a matching sprint, extraction sprint, CRM sprint, or automation
sprint. It is a user experience sprint focused on making existing application
data understandable and actionable.
