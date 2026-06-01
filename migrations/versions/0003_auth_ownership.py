# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""add authentication and ownership

Revision ID: 0003_auth_ownership
Revises: 0002_pipeline_fields
Create Date: 2026-05-31
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0003_auth_ownership"
down_revision: Union[str, None] = "0002_pipeline_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        INSERT INTO users (id, email, display_name, password_hash)
        VALUES (
            '00000000-0000-0000-0000-000000000001',
            'demo-owner@example.com',
            'Demo Owner',
            'migration-placeholder'
        )
        ON CONFLICT (email) DO NOTHING;

        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS auth_audit_events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        ALTER TABLE candidate_profiles
            ADD COLUMN IF NOT EXISTS user_id UUID;
        UPDATE candidate_profiles
            SET user_id = '00000000-0000-0000-0000-000000000001'
            WHERE user_id IS NULL;
        ALTER TABLE candidate_profiles
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE candidate_profiles
            ADD CONSTRAINT fk_candidate_profiles_user
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

        ALTER TABLE match_results
            ADD COLUMN IF NOT EXISTS user_id UUID;
        UPDATE match_results
            SET user_id = COALESCE(
                (
                    SELECT user_id
                    FROM candidate_profiles
                    WHERE candidate_profiles.id = match_results.candidate_profile_id
                ),
                '00000000-0000-0000-0000-000000000001'
            )
            WHERE user_id IS NULL;
        ALTER TABLE match_results
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE match_results
            ADD CONSTRAINT fk_match_results_user
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

        ALTER TABLE interview_briefings
            ADD COLUMN IF NOT EXISTS user_id UUID;
        UPDATE interview_briefings
            SET user_id = COALESCE(
                (
                    SELECT user_id
                    FROM match_results
                    WHERE match_results.id = interview_briefings.match_result_id
                ),
                '00000000-0000-0000-0000-000000000001'
            )
            WHERE user_id IS NULL;
        ALTER TABLE interview_briefings
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE interview_briefings
            ADD CONSTRAINT fk_interview_briefings_user
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

        ALTER TABLE applications
            ADD COLUMN IF NOT EXISTS user_id UUID;
        UPDATE applications
            SET user_id = COALESCE(
                (
                    SELECT user_id
                    FROM candidate_profiles
                    WHERE candidate_profiles.id = applications.candidate_id
                ),
                '00000000-0000-0000-0000-000000000001'
            )
            WHERE user_id IS NULL;
        ALTER TABLE applications
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE applications
            ADD CONSTRAINT fk_applications_user
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

        ALTER TABLE application_notes
            ADD COLUMN IF NOT EXISTS user_id UUID;
        UPDATE application_notes
            SET user_id = COALESCE(
                (
                    SELECT user_id
                    FROM applications
                    WHERE applications.id = application_notes.application_id
                ),
                '00000000-0000-0000-0000-000000000001'
            )
            WHERE user_id IS NULL;
        ALTER TABLE application_notes
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE application_notes
            ADD CONSTRAINT fk_application_notes_user
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

        ALTER TABLE application_outcomes
            ADD COLUMN IF NOT EXISTS user_id UUID;
        UPDATE application_outcomes
            SET user_id = COALESCE(
                (
                    SELECT user_id
                    FROM applications
                    WHERE applications.id = application_outcomes.application_id
                ),
                '00000000-0000-0000-0000-000000000001'
            )
            WHERE user_id IS NULL;
        ALTER TABLE application_outcomes
            ALTER COLUMN user_id SET NOT NULL;
        ALTER TABLE application_outcomes
            ADD CONSTRAINT fk_application_outcomes_user
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

        CREATE TABLE IF NOT EXISTS application_packages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
            package JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS company_intelligence_reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
            report JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id, expires_at DESC);
        CREATE INDEX IF NOT EXISTS idx_auth_audit_events_user ON auth_audit_events(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_candidate_profiles_user ON candidate_profiles(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_match_results_user ON match_results(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_interview_briefings_user ON interview_briefings(user_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_applications_user_candidate ON applications(user_id, candidate_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_applications_user_job ON applications(user_id, job_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_applications_user_status ON applications(user_id, status, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_application_notes_user_application ON application_notes(user_id, application_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_application_outcomes_user_candidate ON application_outcomes(user_id, candidate_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_application_outcomes_user_application ON application_outcomes(user_id, application_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_application_packages_user ON application_packages(user_id, application_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_company_intelligence_reports_user ON company_intelligence_reports(user_id, application_id, created_at DESC);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS company_intelligence_reports;
        DROP TABLE IF EXISTS application_packages;
        DROP TABLE IF EXISTS auth_audit_events;
        DROP TABLE IF EXISTS refresh_tokens;

        DROP INDEX IF EXISTS idx_application_outcomes_user_application;
        DROP INDEX IF EXISTS idx_application_outcomes_user_candidate;
        DROP INDEX IF EXISTS idx_application_notes_user_application;
        DROP INDEX IF EXISTS idx_applications_user_status;
        DROP INDEX IF EXISTS idx_applications_user_job;
        DROP INDEX IF EXISTS idx_applications_user_candidate;
        DROP INDEX IF EXISTS idx_interview_briefings_user;
        DROP INDEX IF EXISTS idx_match_results_user;
        DROP INDEX IF EXISTS idx_candidate_profiles_user;

        ALTER TABLE application_outcomes DROP CONSTRAINT IF EXISTS fk_application_outcomes_user;
        ALTER TABLE application_outcomes DROP COLUMN IF EXISTS user_id;

        ALTER TABLE application_notes DROP CONSTRAINT IF EXISTS fk_application_notes_user;
        ALTER TABLE application_notes DROP COLUMN IF EXISTS user_id;

        ALTER TABLE applications DROP CONSTRAINT IF EXISTS fk_applications_user;
        ALTER TABLE applications DROP COLUMN IF EXISTS user_id;

        ALTER TABLE interview_briefings DROP CONSTRAINT IF EXISTS fk_interview_briefings_user;
        ALTER TABLE interview_briefings DROP COLUMN IF EXISTS user_id;

        ALTER TABLE match_results DROP CONSTRAINT IF EXISTS fk_match_results_user;
        ALTER TABLE match_results DROP COLUMN IF EXISTS user_id;

        ALTER TABLE candidate_profiles DROP CONSTRAINT IF EXISTS fk_candidate_profiles_user;
        ALTER TABLE candidate_profiles DROP COLUMN IF EXISTS user_id;

        DROP TABLE IF EXISTS users;
        """
    )
