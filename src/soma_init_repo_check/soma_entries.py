#!/usr/bin/env python3
"""Build result/skip entry dicts for soma init file processing."""
from __future__ import annotations

from typing import Any
from soma_init_repo_check.types import (
    RepoInfo,
    SkippedNoHostResult,
    SkippedNoRepoResult,
    SkippedNotGithubResult,
)
import sexpdata


def _get_keyword_str(plist: list[Any], keyword: str) -> str | None:
    """Get the string value for a keyword in a plist.

    Input: plist (list of alternating keyword/value), keyword name.
    Output: string value if found, None otherwise.
    """
    for i, item in enumerate(plist):
        if not _is_sym(item, keyword) or i + 1 >= len(plist):
            continue
        val = plist[i + 1]
        if isinstance(val, str):
            return val
    return None


def _get_keyword_sym(plist: list[Any], keyword: str) -> str | None:
    """Get the symbol-name value for a keyword in a plist.

    Input: plist (list of alternating keyword/value), keyword name.
    Output: symbol name string if found, None otherwise.
    """
    for i, item in enumerate(plist):
        if not _is_sym(item, keyword) or i + 1 >= len(plist):
            continue
        val = plist[i + 1]
        if isinstance(val, sexpdata.Symbol):
            return str(val.value())
    return None


def _is_sym(obj: Any, name: str) -> bool:
    """Check if obj is a sexpdata Symbol with the given name."""
    return isinstance(obj, sexpdata.Symbol) and obj.value() == name


def _no_repo_entry(init_file: str) -> SkippedNoRepoResult:
    """Build a skipped:no_repo_directive entry.

    Input: init file name.
    Output: dict with status and init_file.
    """
    return {"status": "skipped:no_repo_directive", "init_file": init_file}


def _no_host_entry(init_file: str, repo: str) -> SkippedNoHostResult:
    """Build a skipped:no_host entry.

    Input: init file name, repo value string.
    Output: dict with status, init_file, and repo.
    """
    return {"status": "skipped:no_host", "init_file": init_file, "repo": repo}


def _not_github_entry(
    repo: str, host: str, init_file: str,
) -> SkippedNotGithubResult:
    """Build a skipped:not_github entry.

    Input: repo value, host symbol name, init file name.
    Output: dict with status, repo, host, and init_file.
    """
    return {
        "status": "skipped:not_github",
        "repo": repo,
        "host": host,
        "init_file": init_file,
    }


def _github_entry(repo_val: str, init_file: str) -> RepoInfo:
    """Build a GitHub repo entry for API checking.

    Input: OWNER/REPO string, init file name.
    Output: dict with owner, repo, host, and init_file.
    """
    parts = repo_val.split("/", 1)
    owner = parts[0] if len(parts) == 2 else ""
    repo = parts[1] if len(parts) == 2 else repo_val
    return {
        "owner": owner,
        "repo": repo,
        "host": "github",
        "init_file": init_file,
    }
