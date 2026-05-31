# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

from uuid import UUID

from psycopg import Connection

from app.feedback import OutcomeRequest, sanitize_notes
from app.matching import MatchResult
from app.schemas import CandidateProfile, JobDescription


def create_candidate(connection: Connection, candidate: CandidateProfile) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO candidate_profiles (
                display_name,
                headline,
                location,
                summary,
                target_roles,
                skills,
                experience_highlights,
                portfolio_links
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                candidate.name,
                candidate.headline,
                candidate.location,
                candidate.summary,
                candidate.target_roles,
                candidate.skills,
                candidate.experience_highlights,
                candidate.portfolio_links,
            ),
        )
        return cursor.fetchone()


def list_candidates(connection: Connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM candidate_profiles ORDER BY created_at DESC")
        return cursor.fetchall()


def get_candidate(connection: Connection, candidate_id: UUID) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM candidate_profiles WHERE id = %s", (candidate_id,))
        return cursor.fetchone()


def create_job(connection: Connection, job: JobDescription) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO job_descriptions (
                title,
                company,
                location,
                description,
                required_skills,
                nice_to_have_skills,
                source,
                source_url,
                external_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                job.title,
                job.company,
                job.location,
                job.description,
                job.required_skills,
                job.nice_to_have_skills,
                job.source,
                job.source_url,
                job.external_id,
            ),
        )
        return cursor.fetchone()


def find_duplicate_job(connection: Connection, job: JobDescription) -> dict | None:
    with connection.cursor() as cursor:
        if job.source_url:
            cursor.execute(
                """
                SELECT *
                FROM job_descriptions
                WHERE source_url = %s
                ORDER BY imported_at DESC, created_at DESC
                LIMIT 1
                """,
                (job.source_url,),
            )
            duplicate = cursor.fetchone()
            if duplicate:
                return duplicate

        cursor.execute(
            """
            SELECT *
            FROM job_descriptions
            WHERE lower(company) = lower(%s)
              AND lower(title) = lower(%s)
              AND COALESCE(lower(location), '') = COALESCE(lower(%s), '')
            ORDER BY imported_at DESC, created_at DESC
            LIMIT 1
            """,
            (job.company, job.title, job.location),
        )
        return cursor.fetchone()


def create_or_get_imported_job(
    connection: Connection,
    job: JobDescription,
) -> tuple[dict, bool]:
    duplicate = find_duplicate_job(connection, job)
    if duplicate:
        return duplicate, True
    return create_job(connection, job), False


def list_jobs(connection: Connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM job_descriptions ORDER BY created_at DESC")
        return cursor.fetchall()


def get_job(connection: Connection, job_id: UUID) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM job_descriptions WHERE id = %s", (job_id,))
        return cursor.fetchone()


def create_match_result(
    connection: Connection,
    candidate_id: UUID,
    job_id: UUID,
    match: MatchResult,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO match_results (
                candidate_profile_id,
                job_description_id,
                score,
                matched_keywords,
                missing_keywords,
                recommendation
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                candidate_id,
                job_id,
                match.score,
                match.matched_keywords,
                match.missing_keywords,
                match.recommendation,
            ),
        )
        return cursor.fetchone()


def list_match_results(connection: Connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM match_results ORDER BY created_at DESC")
        return cursor.fetchall()


def get_match_result(connection: Connection, match_result_id: UUID) -> dict | None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM match_results WHERE id = %s", (match_result_id,))
        return cursor.fetchone()


def create_interview_briefing(
    connection: Connection,
    match_result_id: UUID,
    briefing: dict,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO interview_briefings (
                match_result_id,
                positioning_statement,
                strengths_to_emphasize,
                gaps_to_prepare,
                likely_interview_topics,
                questions_to_ask
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                match_result_id,
                briefing["positioning_statement"],
                briefing["strengths_to_emphasize"],
                briefing["gaps_to_prepare"],
                briefing["likely_interview_topics"],
                briefing["questions_to_ask"],
            ),
        )
        return cursor.fetchone()


def list_interview_briefings(connection: Connection) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM interview_briefings ORDER BY created_at DESC")
        return cursor.fetchall()


def create_application_outcome(
    connection: Connection,
    outcome: OutcomeRequest,
) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO application_outcomes (
                candidate_id,
                job_id,
                application_id,
                outcome,
                notes,
                cv_edits_applied,
                cover_letter_used,
                interview_prep_used,
                skills,
                job_family
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                outcome.candidate_id,
                outcome.job_id,
                outcome.application_id,
                outcome.outcome,
                sanitize_notes(outcome.notes),
                outcome.cv_edits_applied,
                outcome.cover_letter_used,
                outcome.interview_prep_used,
                outcome.skills,
                outcome.job_family,
            ),
        )
        return cursor.fetchone()


def list_application_outcomes(
    connection: Connection,
    candidate_id: UUID,
) -> list[dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT *
            FROM application_outcomes
            WHERE candidate_id = %s
            ORDER BY created_at ASC
            """,
            (candidate_id,),
        )
        return cursor.fetchall()


def candidate_from_row(row: dict) -> CandidateProfile:
    return CandidateProfile(
        name=row["display_name"],
        headline=row["headline"],
        location=row["location"] or "",
        summary=row["summary"],
        target_roles=row["target_roles"],
        skills=row["skills"],
        experience_highlights=row["experience_highlights"],
        portfolio_links=row["portfolio_links"],
    )


def job_from_row(row: dict) -> JobDescription:
    return JobDescription(
        title=row["title"],
        company=row["company"],
        location=row["location"],
        description=row["description"],
        required_skills=row["required_skills"],
        nice_to_have_skills=row["nice_to_have_skills"],
        source=row["source"],
        source_url=row["source_url"],
        external_id=row["external_id"],
    )


def match_from_row(row: dict) -> MatchResult:
    return MatchResult(
        score=row["score"],
        matched_keywords=row["matched_keywords"],
        missing_keywords=row["missing_keywords"],
        candidate_highlights=[],
        recommendation=row["recommendation"],
    )
