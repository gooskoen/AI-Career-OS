-- Copyright 2026 AI-Career-OS contributors
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS candidate_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    display_name TEXT NOT NULL,
    headline TEXT NOT NULL,
    location TEXT,
    summary TEXT NOT NULL,
    target_roles TEXT[] NOT NULL DEFAULT '{}',
    skills TEXT[] NOT NULL DEFAULT '{}',
    experience_highlights TEXT[] NOT NULL DEFAULT '{}',
    portfolio_links TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL DEFAULT '{}',
    nice_to_have_skills TEXT[] NOT NULL DEFAULT '{}',
    source TEXT,
    source_url TEXT,
    external_id TEXT,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS match_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_profile_id UUID NOT NULL REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    job_description_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    matched_keywords TEXT[] NOT NULL DEFAULT '{}',
    missing_keywords TEXT[] NOT NULL DEFAULT '{}',
    recommendation TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS interview_briefings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_result_id UUID NOT NULL REFERENCES match_results(id) ON DELETE CASCADE,
    positioning_statement TEXT NOT NULL,
    strengths_to_emphasize TEXT[] NOT NULL DEFAULT '{}',
    gaps_to_prepare TEXT[] NOT NULL DEFAULT '{}',
    likely_interview_topics TEXT[] NOT NULL DEFAULT '{}',
    questions_to_ask TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'drafted' CHECK (
        status IN (
            'drafted',
            'applied',
            'recruiter_replied',
            'interview_scheduled',
            'interview_completed',
            'rejected',
            'offer_received',
            'hired',
            'withdrawn'
        )
    ),
    source TEXT,
    match_result_id UUID REFERENCES match_results(id) ON DELETE SET NULL,
    application_package_id UUID,
    company_intelligence_id UUID,
    next_action TEXT,
    next_action_due DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS application_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    note TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS application_status_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    previous_status TEXT,
    new_status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS application_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidate_profiles(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES job_descriptions(id) ON DELETE CASCADE,
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    outcome TEXT NOT NULL CHECK (
        outcome IN (
            'applied',
            'recruiter_replied',
            'interview_scheduled',
            'interview_completed',
            'rejected',
            'offer_received',
            'hired',
            'withdrawn'
        )
    ),
    notes TEXT NOT NULL DEFAULT '',
    cv_edits_applied BOOLEAN NOT NULL DEFAULT false,
    cover_letter_used BOOLEAN NOT NULL DEFAULT false,
    interview_prep_used BOOLEAN NOT NULL DEFAULT false,
    skills TEXT[] NOT NULL DEFAULT '{}',
    job_family TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_descriptions_company
    ON job_descriptions(company);

CREATE INDEX IF NOT EXISTS idx_job_descriptions_source_url
    ON job_descriptions(source_url);

CREATE INDEX IF NOT EXISTS idx_job_descriptions_identity
    ON job_descriptions(company, title, location);

CREATE INDEX IF NOT EXISTS idx_match_results_score
    ON match_results(score DESC);

CREATE INDEX IF NOT EXISTS idx_applications_candidate
    ON applications(candidate_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_applications_job
    ON applications(job_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_applications_status
    ON applications(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_applications_next_action_due
    ON applications(next_action_due, status);

CREATE INDEX IF NOT EXISTS idx_application_status_events_application
    ON application_status_events(application_id, created_at ASC);

CREATE INDEX IF NOT EXISTS idx_application_notes_application
    ON application_notes(application_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_application_outcomes_candidate
    ON application_outcomes(candidate_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_application_outcomes_application
    ON application_outcomes(application_id, created_at DESC);
