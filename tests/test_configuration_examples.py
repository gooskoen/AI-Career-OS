# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_database_url_examples_use_psycopg_v3_dialect() -> None:
    checked_files = [
        ROOT / ".env.example",
        ROOT / "docker-compose.yml",
        ROOT / "docs" / "production-installation.md",
    ]

    for path in checked_files:
        content = path.read_text(encoding="utf-8")
        database_url_lines = [
            line.strip()
            for line in content.splitlines()
            if "DATABASE_URL" in line and "postgresql" in line
        ]

        assert database_url_lines, f"{path} should document DATABASE_URL"
        assert all(
            "postgresql+psycopg://" in line
            for line in database_url_lines
        ), f"{path} should use SQLAlchemy's psycopg v3 dialect"


def test_backend_installs_psycopg_v3_not_psycopg2() -> None:
    requirements = (ROOT / "backend" / "requirements.txt").read_text(
        encoding="utf-8"
    )

    assert "psycopg[binary]" in requirements
    assert "psycopg2-binary" not in requirements
