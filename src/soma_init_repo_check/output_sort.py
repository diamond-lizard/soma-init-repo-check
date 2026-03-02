#!/usr/bin/env python3
"""Sort results and errors for JSON output."""
from __future__ import annotations

from urllib.parse import urlparse


def sort_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
    """Sort result entries by init file name, then by OWNER/REPO.

    For deduplicated repos appearing in multiple init files, the
    alphabetically first init file name is the sort key. The elpaca
    bootstrap repo uses 'init.el' as its init file name.

    Input: unsorted list of result entry dicts.
    Output: new sorted list of result entry dicts.
    """
    return sorted(results, key=_result_sort_key)


def sort_errors(errors: list[dict[str, str]]) -> list[dict[str, str]]:
    """Sort error entries by init file name, then by identifier.

    Input: unsorted list of error entry dicts.
    Output: new sorted list of error entry dicts.
    """
    return sorted(errors, key=_error_sort_key)


def _result_sort_key(entry: dict[str, str]) -> tuple[str, str]:
    """Compute sort key for a result entry.

    Primary key: init_file (if present) or 'init.el' for elpaca repos.
    Secondary key: OWNER/REPO extracted from repo_url or repo field.

    Input: result entry dict.
    Output: (init_file, owner_repo) tuple for sorting.
    """
    init_file = entry.get("init_file", "init.el")
    owner_repo = _extract_owner_repo(entry)
    return (init_file, owner_repo)


def _error_sort_key(entry: dict[str, str]) -> tuple[str, str]:
    """Compute sort key for an error entry.

    Primary key: init_file if present, else 'init.el'.
    Secondary key: OWNER/REPO from repo_url or repo field.

    Input: error entry dict.
    Output: (init_file, identifier) tuple for sorting.
    """
    init_file = entry.get("init_file", "init.el")
    identifier = _extract_owner_repo(entry)
    return (init_file, identifier)


def _extract_owner_repo(entry: dict[str, str]) -> str:
    """Extract OWNER/REPO from a result or error entry.

    Checks repo_url first (parses URL path), then repo field.
    Falls back to empty string if neither is present.

    Input: entry dict that may have repo_url or repo keys.
    Output: OWNER/REPO string for sorting.
    """
    repo_url = entry.get("repo_url", "")
    if repo_url:
        path = urlparse(repo_url).path.strip("/")
        return path
    return entry.get("repo", "")
