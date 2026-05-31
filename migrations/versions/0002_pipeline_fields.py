# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

"""add application pipeline fields

Revision ID: 0002_pipeline_fields
Revises: 0001_baseline
Create Date: 2026-05-31
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0002_pipeline_fields"
down_revision: Union[str, None] = "0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE applications
            ADD COLUMN IF NOT EXISTS next_action TEXT,
            ADD COLUMN IF NOT EXISTS next_action_due DATE;

        CREATE INDEX IF NOT EXISTS idx_applications_next_action_due
            ON applications(next_action_due, status);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_applications_next_action_due;

        ALTER TABLE applications
            DROP COLUMN IF EXISTS next_action_due,
            DROP COLUMN IF EXISTS next_action;
        """
    )
