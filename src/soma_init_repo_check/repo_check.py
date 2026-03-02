#!/usr/bin/env python3
"""Orchestrate repo-info and compare API calls for a single repo."""
from __future__ import annotations

from typing import Any

from soma_init_repo_check.api import fetch_compare
from soma_init_repo_check.api import fetch_repo_info
from soma_init_repo_check.types import ErrorEntry
from soma_init_repo_check.types import ForkResult
from soma_init_repo_check.types import ResultEntry
from soma_init_repo_check.types import SkippedNotAForkResult


def check_repo(
    session: Any, owner: str, repo: str,
) -> tuple[ResultEntry | None, ErrorEntry | None]:
    """Check a single GitHub repo's fork status and compare branches.

    If get-repo-info succeeds and identifies a fork, but the compare
    call fails, the repo is recorded in errors (not results), since
    a fork result requires both ahead_by and behind_by values.

    Input: session -- CachedSession.
           owner, repo -- repo identifiers.
    Output: (result_entry, None) on success,
            (None, error_entry) on any failure.
    """
    repo_url = f"https://github.com/{owner}/{repo}"
    info, err = fetch_repo_info(session, owner, repo)
    if err:
        return None, {"repo_url": repo_url, "error": err}
    if info is None:
        return None, {"repo_url": repo_url, "error": "No info returned"}
    if not info["fork"]:
        result: SkippedNotAForkResult = {
            "status": "skipped:not_a_fork",
            "repo_url": repo_url,
        }
        return result, None
    return _check_fork_compare(session, info, owner, repo, repo_url)


def _check_fork_compare(
    session: Any,
    info: dict[str, Any],
    owner: str,
    repo: str,
    repo_url: str,
) -> tuple[ResultEntry | None, ErrorEntry | None]:
    """Compare branches for a confirmed fork.

    If compare fails, the repo goes to errors, not results.

    Input: session -- CachedSession. info -- repo info dict.
           owner, repo -- identifiers. repo_url -- canonical URL.
    Output: (ForkResult, None) or (None, ErrorEntry).
    """
    cmp, cmp_err = fetch_compare(
        session,
        info["parent_owner"],
        info["parent_repo"],
        info["parent_default_branch"],
        owner,
        info["fork_default_branch"],
    )
    if cmp_err:
        return None, {"repo_url": repo_url, "error": cmp_err}
    if cmp is None:
        return None, {"repo_url": repo_url, "error": "No compare data"}
    result: ForkResult = {
        "status": "fork",
        "repo_url": repo_url,
        "ahead_by": cmp["ahead_by"],
        "behind_by": cmp["behind_by"],
    }
    return result, None
