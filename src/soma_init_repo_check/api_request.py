#!/usr/bin/env python3
"""Shared HTTP request helper with rate limit retry for GitHub API."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests
    import requests_cache

from tenacity import Retrying

from soma_init_repo_check.rate_retry import RateLimitWait
from soma_init_repo_check.rate_retry import should_retry_rate_limit
from soma_init_repo_check.rate_retry import stop_after_rate_limit_retries

API_BASE = "https://api.github.com"
TIMEOUT = 30
_requested_urls: set[str] = set()


def request(session: requests_cache.CachedSession, url: str) -> requests.Response:
    """Make an API request with rate limit retry via tenacity.

    Creates a fresh Retrying instance per request with rate limit
    wait/retry/stop callbacks. Returns the raw requests.Response.

    Input: session -- CachedSession. url -- fully constructed API URL.
    Output: requests.Response from the API.
    Raises: tenacity.RetryError if rate limit retries exhausted.
    """
    _requested_urls.add(url)
    retryer = Retrying(
        retry=should_retry_rate_limit,
        wait=RateLimitWait(),
        stop=stop_after_rate_limit_retries,
    )
    return retryer(session.get, url, timeout=TIMEOUT)


def get_requested_urls() -> frozenset[str]:
    """Return the set of URLs requested during this process run.

    Input: None.
    Output: frozenset of URL strings requested via request().
    """
    return frozenset(_requested_urls)
