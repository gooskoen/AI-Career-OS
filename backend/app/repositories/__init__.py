# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from app.repositories.applications import (
    application_artifact_readiness,
    application_board,
    application_summary,
    create_application,
    create_application_note,
    get_application,
    latest_application_notes,
    latest_application_outcome,
    list_application_status_events,
    list_applications,
    update_application_next_action,
    update_application_status,
)
from app.repositories.candidates import (
    candidate_from_row,
    create_candidate,
    get_candidate,
    list_candidates,
)
from app.repositories.jobs import (
    create_job,
    create_or_get_imported_job,
    find_duplicate_job,
    get_job,
    job_from_row,
    list_jobs,
)
from app.repositories.matching import (
    create_interview_briefing,
    create_match_result,
    get_match_result,
    list_interview_briefings,
    list_match_results,
    match_from_row,
)
from app.repositories.outcomes import (
    create_application_outcome,
    list_application_outcomes,
)

__all__ = [
    "candidate_from_row",
    "application_artifact_readiness",
    "application_board",
    "application_summary",
    "create_application",
    "create_application_note",
    "create_application_outcome",
    "create_candidate",
    "create_interview_briefing",
    "create_job",
    "create_match_result",
    "create_or_get_imported_job",
    "find_duplicate_job",
    "get_application",
    "get_candidate",
    "get_job",
    "get_match_result",
    "job_from_row",
    "latest_application_notes",
    "latest_application_outcome",
    "list_application_outcomes",
    "list_application_status_events",
    "list_applications",
    "list_candidates",
    "list_interview_briefings",
    "list_jobs",
    "list_match_results",
    "match_from_row",
    "update_application_next_action",
    "update_application_status",
]
