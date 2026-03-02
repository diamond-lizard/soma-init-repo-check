#!/usr/bin/env python3
"""HTTP error classification, retry logic, and network error handling."""
from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse


_5XX_RETRY_DELAY = 5.0


def classify_http_error(status_code: int, owner_repo: str) -> str:
    """Build a descriptive error message for a non-200 HTTP response.

    404 errors include a note about possible deleted repo or
    insufficient token permissions. Other errors use generic format.

    Input: status_code -- HTTP status code.
           owner_repo -- "OWNER/REPO" for error context.
    Output: descriptive error message string.
    """
    if status_code == 404:
        return (
            f"HTTP 404 for {owner_repo}: "
            "repo may be deleted or token may lack permissions"
        )
    return f"HTTP {status_code} for {owner_repo}"


def is_server_error(status_code: int) -> bool:
    """Check whether an HTTP status code is a 5xx server error.

    Input: status_code -- HTTP status code.
    Output: True if 5xx, False otherwise.
    """
    return 500 <= status_code < 600


def retry_server_error(session: Any, url: str) -> Any:
    """Retry a failed request once after a 5-second delay.

    Uses the standard request mechanism including rate limit retry
    via tenacity. If the retry gets rate-limited, tenacity handles it.

    Input: session -- CachedSession. url -- original request URL.
    Output: requests.Response from the retry attempt.
    """
    from soma_init_repo_check.api_request import request

    time.sleep(_5XX_RETRY_DELAY)
    return request(session, url)


def classify_network_error(exc: Exception, owner_repo: str) -> str:
    """Build a descriptive error message for a network-level failure.

    Covers timeout, connection, DNS, and SSL errors. Uses the
    exception type name and message for diagnostics.

    Input: exc -- the caught exception.
           owner_repo -- "OWNER/REPO" for error context.
    Output: descriptive error message string.
    """
    exc_type = type(exc).__name__
    return f"{exc_type} for {owner_repo}: {exc}"


def extract_host(url: str) -> str:
    """Extract the hostname from a URL for per-host error counting.

    Input: url -- a fully-qualified URL string.
    Output: hostname string (e.g., 'api.github.com').
    """
    return urlparse(url).hostname or "unknown"
