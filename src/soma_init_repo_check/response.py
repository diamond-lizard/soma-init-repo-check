#!/usr/bin/env python3
"""Response processing pipeline for GitHub API responses."""
from __future__ import annotations

import json
from typing import Any


_MAX_RESPONSE_BYTES = 10 * 1024 * 1024
_CHUNK_SIZE = 8192


def _check_content_length(response: Any) -> str | None:
    """Reject responses whose Content-Length exceeds 10 MB.

    Input: response — a requests.Response object.
    Output: error string if too large, None if acceptable.
    """
    cl = response.headers.get("Content-Length")
    if cl is not None and cl.isdigit() and int(cl) > _MAX_RESPONSE_BYTES:
        return f"Response too large: Content-Length {cl} exceeds 10 MB"
    return None


def _check_content_type(response: Any) -> str | None:
    """Reject responses whose Content-Type does not indicate JSON.

    Input: response — a requests.Response object.
    Output: error string if not JSON, None if acceptable.
    """
    ct = response.headers.get("Content-Type", "")
    if "json" not in ct.lower():
        return f"Unexpected Content-Type: {ct}"
    return None


def _read_body(response: Any) -> tuple[bytes, str | None]:
    """Read the response body via streaming with a size limit.

    Input: response — a requests.Response object.
    Output: (body_bytes, error_string_or_None).
    """
    chunks: list[bytes] = []
    total = 0
    for chunk in response.iter_content(chunk_size=_CHUNK_SIZE):
        total += len(chunk)
        if total > _MAX_RESPONSE_BYTES:
            return b"", "Response body exceeds 10 MB during streaming"
        chunks.append(chunk)
    return b"".join(chunks), None


def process_response(response: Any) -> tuple[Any | None, str | None]:
    """Process an API response through the validation pipeline.

    Steps: (1) Content-Length check, (2) Content-Type check,
    (3) streaming body read with size limit, (4) JSON parse.

    Input: response — a requests.Response object.
    Output: (parsed_json, None) on success, (None, error_string) on failure.
    """
    err = _check_content_length(response)
    if err:
        return None, err
    err = _check_content_type(response)
    if err:
        return None, err
    body, err = _read_body(response)
    if err:
        return None, err
    try:
        return json.loads(body), None
    except (json.JSONDecodeError, ValueError) as exc:
        return None, f"Invalid JSON: {exc}"
