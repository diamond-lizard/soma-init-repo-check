#!/usr/bin/env python3
"""TypeGuard-based accessors for ResultEntry and ErrorEntry unions."""
from __future__ import annotations

from typing import TypeGuard

from soma_init_repo_check.types import (
    ApiErrorEntry,
    ErrorEntry,
    ForkResult,
    ResultEntry,
    SkippedNoHostResult,
    SkippedNoRepoResult,
    SkippedNotAForkResult,
    SkippedNotGithubResult,
)


def _has_init_file(
    entry: ResultEntry | ErrorEntry,
) -> TypeGuard[
    SkippedNotGithubResult | SkippedNoRepoResult | SkippedNoHostResult
]:
    """Check if entry has an init_file field."""
    return "init_file" in entry


def _has_repo_url(
    entry: ResultEntry | ErrorEntry,
) -> TypeGuard[ForkResult | SkippedNotAForkResult | ApiErrorEntry]:
    """Check if entry has a repo_url field."""
    return "repo_url" in entry


def _has_repo(
    entry: ResultEntry | ErrorEntry,
) -> TypeGuard[SkippedNotGithubResult | SkippedNoHostResult]:
    """Check if entry has a repo field."""
    return "repo" in entry


def _is_fork(entry: ResultEntry) -> TypeGuard[ForkResult]:
    """Check if entry is a ForkResult."""
    return entry.get("status") == "fork"


def get_status(entry: ResultEntry) -> str:
    """Get status from a result entry.

    All ResultEntry members have a status field.

    Input: a ResultEntry.
    Output: status string.
    """
    return entry["status"]


def get_init_file(entry: ResultEntry | ErrorEntry) -> str:
    """Get init_file from an entry, defaulting to 'init.el'.

    Input: a ResultEntry or ErrorEntry.
    Output: init_file string, or 'init.el' for entries without one.
    """
    if _has_init_file(entry):
        return entry["init_file"]
    return "init.el"


def get_repo_url(entry: ResultEntry | ErrorEntry) -> str:
    """Get repo_url from an entry, defaulting to empty string.

    Input: a ResultEntry or ErrorEntry.
    Output: repo_url string, or '' for entries without one.
    """
    if _has_repo_url(entry):
        return entry["repo_url"]
    return ""


def get_repo(entry: ResultEntry | ErrorEntry) -> str:
    """Get repo from an entry, defaulting to empty string.

    Input: a ResultEntry or ErrorEntry.
    Output: repo string, or '' for entries without one.
    """
    if _has_repo(entry):
        return entry["repo"]
    return ""


def is_fork_behind(entry: ResultEntry) -> bool:
    """Check if entry is a fork that is behind upstream.

    Input: a ResultEntry.
    Output: True if fork with behind_by > 0.
    """
    if _is_fork(entry):
        return entry["behind_by"] > 0
    return False
