#!/usr/bin/env python3
"""Shared HTTP request helper with rate limit retry for GitHub API."""
from __future__ import annotations

from typing import Any

from tenacity import Retrying

from soma_init_repo_check.rate_retry import RateLimitWait
from soma_init_repo_check.rate_retry import should_retry_rate_limit
from soma_init_repo_check.rate_retry import stop_after_rate_limit_retries

API_BASE = "https://api.github.com"
TIMEOUT = 30


def request(session: Any, url: str) -> Any:
    """Make an API request with rate limit retry via tenacity.

    Creates a fresh Retrying instance per request with rate limit
    wait/retry/stop callbacks. Returns the raw requests.Response.

    Input: session -- CachedSession. url -- fully constructed API URL.
    Output: requests.Response from the API.
    Raises: tenacity.RetryError if rate limit retries exhausted.
    """
    retryer = Retrying(
        retry=should_retry_rate_limit,
        wait=RateLimitWait(),
        stop=stop_after_rate_limit_retries,
    )
    return retryer(session.get, url, timeout=TIMEOUT)
