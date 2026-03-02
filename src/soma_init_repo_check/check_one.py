#!/usr/bin/env python3
"""Check a single repo with 5xx retry and network error handling."""
from __future__ import annotations

import time
from typing import Any

from tenacity import RetryError

from soma_init_repo_check.errors import classify_network_error
from soma_init_repo_check.repo_check import check_repo

_5XX_DELAY = 5.0


def check_one(
    session: Any,
    owner: str,
    repo: str,
    owner_repo: str,
    is_retry: bool = False,
) -> tuple[dict[str, Any] | None, dict[str, str] | None, int]:
    """Check one repo with 5xx retry and exception handling.

    Makes the API call via check_repo. On network exceptions,
    classifies the error. On 5xx errors (first attempt only),
    waits 5 seconds and retries once. RetryError from tenacity
    (rate limit exhaustion) is re-raised to the caller.

    Input: session -- CachedSession for API calls.
           owner -- GitHub owner string.
           repo -- GitHub repo name string.
           owner_repo -- "OWNER/REPO" for error messages.
           is_retry -- True if this is a 5xx retry attempt.
    Output: (result_or_None, error_or_None, error_count).
            error_count is 0 on success, 1 on first failure,
            2 on retry failure.
    """
    repo_url = f"https://github.com/{owner_repo}"
    err_n = 2 if is_retry else 1
    try:
        result, error = check_repo(session, owner, repo)
    except RetryError:
        raise
    except Exception as exc:
        msg = classify_network_error(exc, owner_repo)
        return None, {"repo_url": repo_url, "error": msg}, err_n
    if error is None:
        return result, None, 0
    if not is_retry and _is_5xx(error.get("error", "")):
        time.sleep(_5XX_DELAY)
        return check_one(session, owner, repo, owner_repo, True)
    return None, error, err_n


def _is_5xx(msg: str) -> bool:
    """Check if an error message indicates a 5xx server error.

    Parses the HTTP status code from messages like "HTTP 502 for ...".

    Input: msg -- error message string from check_repo.
    Output: True if the status code is in the 500-599 range.
    """
    if not msg.startswith("HTTP "):
        return False
    parts = msg.split(" ", 2)
    try:
        return 500 <= int(parts[1]) < 600
    except (ValueError, IndexError):
        return False
