#!/usr/bin/env python3
"""Tests for rate limit classification."""
from __future__ import annotations

import json
import requests
from io import BytesIO


from soma_init_repo_check.rate_limit import is_rate_limited


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


def test_403_with_remaining_zero_is_rate_limited() -> None:
    """A 403 with x-ratelimit-remaining: 0 is a rate limit."""
    resp = _make_response(403, {"x-ratelimit-remaining": "0"})
    assert is_rate_limited(resp) is True


def test_429_with_remaining_zero_is_rate_limited() -> None:
    """A 429 with x-ratelimit-remaining: 0 is a rate limit."""
    resp = _make_response(429, {"x-ratelimit-remaining": "0"})
    assert is_rate_limited(resp) is True


def test_429_secondary_rate_limit_message() -> None:
    """A 429 with secondary rate limit message is a rate limit."""
    body = {"message": "You have exceeded a secondary rate limit"}
    resp = _make_response(429, body=body)
    assert is_rate_limited(resp) is True


def test_403_without_indicators_is_genuine_error() -> None:
    """A 403 without rate limit indicators is a genuine error."""
    resp = _make_response(403, body={"message": "Resource not accessible"})
    assert is_rate_limited(resp) is False


def test_200_is_not_rate_limited() -> None:
    """A 200 response is never rate-limited."""
    resp = _make_response(200)
    assert is_rate_limited(resp) is False

