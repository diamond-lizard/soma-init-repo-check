#!/usr/bin/env python3
"""Tenacity callbacks for rate limit retry logic."""
from __future__ import annotations

from tenacity import RetryCallState

from soma_init_repo_check.rate_limit import compute_wait_time
from soma_init_repo_check.rate_limit import is_rate_limited


_MAX_RATE_RETRIES = 10


def should_retry_rate_limit(retry_state: RetryCallState) -> bool:
    """Tenacity retry callback: retry only if the response is rate-limited.

    Input: retry_state -- tenacity RetryCallState.
    Output: True to retry, False to stop.
    """
    if retry_state.outcome is None:
        return False
    if retry_state.outcome.failed:
        return False
    response = retry_state.outcome.result()
    return is_rate_limited(response)


class RateLimitWait:
    """Callable wait strategy with exponential backoff for rate limits.

    First retry: uses header-derived wait time from the response.
    Subsequent retries: uses the greater of the header-suggested wait
    and exponential backoff (doubling previous wait each time).
    """

    def __init__(self) -> None:
        """Initialize with no previous wait recorded."""
        self._prev_wait: float = 0.0

    def __call__(self, retry_state: RetryCallState) -> float:
        """Compute the wait time for the current retry attempt.

        Input: retry_state -- tenacity RetryCallState.
        Output: seconds to wait before retrying (float).
        """
        if retry_state.outcome is None:
            return 60.0
        response = retry_state.outcome.result()
        header_wait = compute_wait_time(response)
        if retry_state.attempt_number == 1:
            self._prev_wait = header_wait
            return header_wait
        backoff = self._prev_wait * 2
        wait = max(header_wait, backoff)
        self._prev_wait = wait
        return wait

    def reset(self) -> None:
        """Reset state between requests.

        The retry counter resets on each successful request.
        Output: None.
        """
        self._prev_wait = 0.0


def stop_after_rate_limit_retries(retry_state: RetryCallState) -> bool:
    """Tenacity stop callback: stop after max consecutive rate-limit retries.

    Input: retry_state -- tenacity RetryCallState.
    Output: True to stop retrying, False to continue.
    """
    return bool(retry_state.attempt_number >= _MAX_RATE_RETRIES)
