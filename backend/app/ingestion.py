# Copyright 2026 AI-Career-OS contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

from __future__ import annotations

import html
import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from app.repositories import create_job
from app.schemas import JobDescription

MAX_RESPONSE_BYTES = 1_000_000
REQUEST_TIMEOUT_SECONDS = 8
KNOWN_SKILLS = [
    "ai strategy",
    "analytics",
    "api",
    "automation",
    "fastapi",
    "leadership",
    "postgresql",
    "prompt engineering",
    "python",
    "responsible ai",
    "sql",
    "stakeholder management",
    "workflow automation",
]


class IngestionError(ValueError):
    """Raised when a job import request cannot be safely processed."""


class UrlFetchError(RuntimeError):
    """Raised when a safe URL cannot be fetched."""


class _ReadableTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._hidden_depth = 0
        self._chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self._hidden_depth += 1
        if tag in {"br", "div", "h1", "h2", "h3", "li", "p", "section"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._hidden_depth:
            self._hidden_depth -= 1
        if tag in {"div", "h1", "h2", "h3", "li", "p", "section"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._hidden_depth:
            self._chunks.append(data)

    def text(self) -> str:
        return html.unescape(" ".join(self._chunks))


def normalize_job_text(raw_text: str) -> str:
    text = html.unescape(raw_text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    meaningful_lines = [line for line in lines if line]
    return "\n".join(meaningful_lines)


def extract_job_from_text(
    raw_text: str,
    source_url: str | None = None,
) -> JobDescription:
    description = normalize_job_text(raw_text)
    if not description:
        raise IngestionError("Job text is empty after normalization")

    title = _first_meaningful_line(description)
    return JobDescription(
        title=title,
        company="Unknown",
        description=description,
        required_skills=_extract_known_skills(description),
        nice_to_have_skills=[],
        source_url=source_url,
    )


def import_job_from_text(
    connection,
    raw_text: str,
    source_url: str | None = None,
) -> dict:
    job = extract_job_from_text(raw_text, source_url)
    return create_job(connection, job)


def import_job_from_url(connection, url: str) -> dict:
    _validate_public_http_url(url)
    raw_text = _fetch_url_text(url)
    job = extract_job_from_text(raw_text, source_url=url)
    return create_job(connection, job)


def _first_meaningful_line(text: str) -> str:
    for line in text.splitlines():
        if len(line) >= 4:
            return line[:160]
    return "Untitled job"


def _extract_known_skills(text: str) -> list[str]:
    lowered = text.lower()
    return sorted({skill for skill in KNOWN_SKILLS if skill in lowered})


def _fetch_url_text(url: str) -> str:
    request = Request(
        url,
        headers={"User-Agent": "AI-Career-OS/0.1 job-ingestion"},
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            content_type = response.headers.get("content-type", "")
            content = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise IngestionError(f"URL returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise UrlFetchError("Unable to fetch URL") from exc
    except TimeoutError as exc:
        raise UrlFetchError("URL fetch timed out") from exc

    if len(content) > MAX_RESPONSE_BYTES:
        raise IngestionError("URL response is too large")

    decoded = content.decode(_charset_from_content_type(content_type), errors="replace")
    if "html" in content_type.lower() or _looks_like_html(decoded):
        return _html_to_text(decoded)
    return decoded


def _validate_public_http_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise IngestionError("Only http and https URLs are supported")
    if not parsed.hostname:
        raise IngestionError("URL must include a hostname")
    if parsed.username or parsed.password:
        raise IngestionError("Credentialed URLs are not supported")

    hostname = parsed.hostname.lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        raise IngestionError("Localhost URLs are not allowed")

    try:
        addresses = socket.getaddrinfo(hostname, parsed.port or _default_port(parsed.scheme))
    except socket.gaierror as exc:
        raise IngestionError("URL hostname could not be resolved") from exc

    for address in addresses:
        ip_address = ipaddress.ip_address(address[4][0])
        if not ip_address.is_global:
            raise IngestionError("Private or local network URLs are not allowed")


def _default_port(scheme: str) -> int:
    return 443 if scheme == "https" else 80


def _charset_from_content_type(content_type: str) -> str:
    match = re.search(r"charset=([\w.-]+)", content_type, flags=re.IGNORECASE)
    return match.group(1) if match else "utf-8"


def _looks_like_html(text: str) -> bool:
    return bool(re.search(r"<\s*(html|body|div|p|h1|section)\b", text, re.IGNORECASE))


def _html_to_text(raw_html: str) -> str:
    parser = _ReadableTextParser()
    parser.feed(raw_html)
    return normalize_job_text(parser.text())
