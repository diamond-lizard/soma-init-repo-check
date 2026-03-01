#!/usr/bin/env python3
"""Rate limit detection, wait time computation, and tenacity callbacks."""
from __future__ import annotations

import time
import sys
import requests


def is_rate_limited(response: requests.Response) -> bool:
    """Determine whether an HTTP response indicates a rate limit.

    Checks: (1) status 403/429 with x-ratelimit-remaining: 0,
    (2) response body message containing "secondary rate limit".
    Rate limit responses must not count toward the per-host error threshold.

    Input: response -- a requests.Response object.
    Output: True if rate-limited, False if a genuine error.
    """
    status = response.status_code
    remaining = response.headers.get("x-ratelimit-remaining")
    if status in (403, 429) and remaining == "0":
        return True
    if status in (403, 429):
        try:
            body = response.json()
        except Exception:
            return False
        msg = body.get("message", "") if isinstance(body, dict) else ""
        if "secondary rate limit" in msg.lower():
            return True
    return False


def compute_wait_time(response: requests.Response) -> float:
    """Compute how long to wait before retrying a rate-limited response.

    Priority: (a) x-ratelimit-reset epoch timestamp minus now,
    (b) retry-after header seconds, (c) default 60 seconds.
    Applies floor of max(1, wait) to prevent negative or zero waits.

    Input: response -- a requests.Response object.
    Output: wait time in seconds (float, >= 1.0).
    """
    remaining = response.headers.get("x-ratelimit-remaining")
    reset_hdr = response.headers.get("x-ratelimit-reset")
    if remaining == "0" and reset_hdr is not None:
        try:
            reset_ts = int(reset_hdr)
            wait = reset_ts - time.time()
            return max(1.0, wait)
        except (ValueError, TypeError):
            pass
    retry_after = response.headers.get("retry-after")
    if retry_after is not None:
        try:
            return max(1.0, float(retry_after))
        except (ValueError, TypeError):
            pass
    return 60.0


def notify_rate_limit(wait_seconds: float, quiet: bool) -> None:
    """Print a rate limit notification to stderr.

    Informs the user that a rate limit was hit and how long the
    program will wait before retrying. Suppressed by --quiet.

    Input: wait_seconds -- how long the program will wait.
        quiet -- if True, suppress the notification.
    Output: None. Prints to stderr as a side effect.
    """
    if quiet:
        return
    print(
        f"Rate limited. Waiting {int(wait_seconds)}s before retrying...",
        file=sys.stderr,
    )


_INTER_REQUEST_DELAY = 0.1


def inter_request_delay() -> None:
    """Apply the 100ms delay between non-rate-limited API requests.

    Reduces the risk of triggering secondary rate limits.
    Output: None. Sleeps as a side effect.
    """
    time.sleep(_INTER_REQUEST_DELAY)
