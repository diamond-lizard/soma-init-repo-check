#!/usr/bin/env python3
"""Tests for tenacity retry callbacks and exponential backoff."""
from __future__ import annotations

import json
import requests
from io import BytesIO
from unittest.mock import MagicMock

from tenacity import RetryCallState

from soma_init_repo_check.rate_retry import RateLimitWait
from soma_init_repo_check.rate_retry import should_retry_rate_limit
from soma_init_repo_check.rate_retry import stop_after_rate_limit_retries


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


def _make_retry_state(
    response: requests.Response,
    attempt: int = 1,
) -> RetryCallState:
    """Build a mock RetryCallState with a completed outcome."""
    future: MagicMock = MagicMock()
    future.failed = False
    future.result.return_value = response
    state = MagicMock(spec=RetryCallState)
    state.outcome = future
    state.attempt_number = attempt
    return state


def test_should_retry_on_rate_limited_response() -> None:
    """Retry callback returns True for a rate-limited response."""
    resp = _make_response(429, {"x-ratelimit-remaining": "0"})
    state = _make_retry_state(resp)
    assert should_retry_rate_limit(state) is True


def test_should_not_retry_on_genuine_error() -> None:
    """Retry callback returns False for a non-rate-limited response."""
    resp = _make_response(404)
    state = _make_retry_state(resp)
    assert should_retry_rate_limit(state) is False


def test_should_not_retry_when_outcome_is_none() -> None:
    """Retry callback returns False when outcome is None."""
    state = MagicMock(spec=RetryCallState)
    state.outcome = None
    assert should_retry_rate_limit(state) is False


def test_stop_after_10_retries() -> None:
    """Stop callback returns True after 10 attempts."""
    resp = _make_response(429, {"x-ratelimit-remaining": "0"})
    state = _make_retry_state(resp, attempt=10)
    assert stop_after_rate_limit_retries(state) is True


def test_do_not_stop_before_10_retries() -> None:
    """Stop callback returns False before 10 attempts."""
    resp = _make_response(429, {"x-ratelimit-remaining": "0"})
    state = _make_retry_state(resp, attempt=9)
    assert stop_after_rate_limit_retries(state) is False


def test_exponential_backoff_doubles_previous_wait() -> None:
    """Backoff uses the greater of header wait and doubled previous."""
    resp = _make_response(429, {"retry-after": "10"})
    waiter = RateLimitWait()
    state1 = _make_retry_state(resp, attempt=1)
    w1 = waiter(state1)
    assert w1 == 10.0
    state2 = _make_retry_state(resp, attempt=2)
    w2 = waiter(state2)
    assert w2 == 20.0
    state3 = _make_retry_state(resp, attempt=3)
    w3 = waiter(state3)
    assert w3 == 40.0
