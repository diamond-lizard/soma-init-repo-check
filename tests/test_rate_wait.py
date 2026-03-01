#!/usr/bin/env python3
"""Tests for rate limit wait time computation."""
from __future__ import annotations

import json
import requests
import time
from io import BytesIO

from soma_init_repo_check.rate_limit import compute_wait_time


def _make_response(
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    body: dict[str, str] | None = None,
) -> requests.Response:
    """Build a requests.Response with controlled status, headers, body."""
    resp = requests.Response()
    resp.status_code = status_code
    if headers:
        resp.headers.update(headers)
    content = json.dumps(body or {}).encode()
    resp.headers.setdefault("Content-Type", "application/json")
    resp.raw = BytesIO(content)
    resp._content = content
    return resp


def test_wait_uses_ratelimit_reset_header() -> None:
    """Wait time uses x-ratelimit-reset when remaining is 0."""
    future_ts = str(int(time.time()) + 30)
    resp = _make_response(429, {
        "x-ratelimit-remaining": "0",
        "x-ratelimit-reset": future_ts,
    })
    wait = compute_wait_time(resp)
    assert 28.0 <= wait <= 32.0


def test_wait_uses_retry_after_header() -> None:
    """Wait time uses retry-after when reset is absent."""
    resp = _make_response(429, {"retry-after": "45"})
    assert compute_wait_time(resp) == 45.0


def test_wait_defaults_to_60_seconds() -> None:
    """Default 60s wait when no relevant headers are present."""
    resp = _make_response(429)
    assert compute_wait_time(resp) == 60.0


def test_wait_fallback_when_reset_unparseable() -> None:
    """Falls back to retry-after when x-ratelimit-reset is unparseable."""
    resp = _make_response(429, {
        "x-ratelimit-remaining": "0",
        "x-ratelimit-reset": "not-a-number",
        "retry-after": "20",
    })
    assert compute_wait_time(resp) == 20.0


def test_wait_floor_prevents_negative() -> None:
    """max(1, wait) floor applied when reset is in the past."""
    past_ts = str(int(time.time()) - 100)
    resp = _make_response(429, {
        "x-ratelimit-remaining": "0",
        "x-ratelimit-reset": past_ts,
    })
    assert compute_wait_time(resp) == 1.0


def test_wait_fallback_when_remaining_not_zero() -> None:
    """Falls back to retry-after when x-ratelimit-remaining is not 0."""
    resp = _make_response(429, {
        "x-ratelimit-remaining": "5",
        "x-ratelimit-reset": str(int(time.time()) + 100),
        "retry-after": "10",
    })
    assert compute_wait_time(resp) == 10.0
