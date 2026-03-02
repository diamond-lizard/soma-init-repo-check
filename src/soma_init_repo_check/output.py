#!/usr/bin/env python3
"""Construct JSON output entries and assemble the final output structure."""
from __future__ import annotations

from soma_init_repo_check.types import ForkResult
from soma_init_repo_check.types import SkippedNotAForkResult
from soma_init_repo_check.types import SkippedNotGithubResult
from soma_init_repo_check.types import SkippedNoRepoResult
from soma_init_repo_check.types import SkippedNoHostResult


def make_repo_url(owner: str, repo: str) -> str:
    """Build the canonical GitHub URL for a repo.

    Input: owner -- GitHub username/org. repo -- repository name.
    Output: URL string like 'https://github.com/OWNER/REPO'.
    """
    return f"https://github.com/{owner}/{repo}"


def fork_entry(
    owner: str, repo: str, ahead_by: int, behind_by: int,
) -> ForkResult:
    """Construct a fork result entry.

    Input: owner, repo -- GitHub identifiers.
           ahead_by, behind_by -- commit count integers.
    Output: ForkResult dict with status, repo_url, ahead_by, behind_by.
    """
    return {
        "status": "fork",
        "repo_url": make_repo_url(owner, repo),
        "ahead_by": ahead_by,
        "behind_by": behind_by,
    }


def not_a_fork_entry(owner: str, repo: str) -> SkippedNotAForkResult:
    """Construct a skipped:not_a_fork result entry.

    Input: owner, repo -- GitHub identifiers.
    Output: SkippedNotAForkResult dict with status and repo_url.
    """
    return {
        "status": "skipped:not_a_fork",
        "repo_url": make_repo_url(owner, repo),
    }


def not_github_entry(repo: str, host: str) -> SkippedNotGithubResult:
    """Construct a skipped:not_github result entry.

    Input: repo -- OWNER/REPO string. host -- short host identifier.
    Output: SkippedNotGithubResult dict with status, repo, host.
    """
    return {"status": "skipped:not_github", "repo": repo, "host": host}


def no_repo_entry(init_file: str) -> SkippedNoRepoResult:
    """Construct a skipped:no_repo_directive result entry.

    Input: init_file -- the init file name.
    Output: SkippedNoRepoResult dict with status and init_file.
    """
    return {"status": "skipped:no_repo_directive", "init_file": init_file}


def no_host_entry(init_file: str, repo: str) -> SkippedNoHostResult:
    """Construct a skipped:no_host result entry.

    Input: init_file -- the init file name. repo -- repo value string.
    Output: SkippedNoHostResult dict with status, init_file, repo.
    """
    return {"status": "skipped:no_host", "init_file": init_file, "repo": repo}


def api_error_entry(repo_url: str, error: str) -> dict[str, str]:
    """Build an error entry for an API or network failure.

    Input: repo_url -- canonical GitHub URL. error -- description.
    Output: dict with repo_url and error keys.
    """
    return {"repo_url": repo_url, "error": error}


def init_file_error_entry(init_file: str, error: str) -> dict[str, str]:
    """Build an error entry for a missing or unreadable init file.

    Input: init_file -- init file name. error -- description.
    Output: dict with init_file and error keys.
    """
    return {"init_file": init_file, "error": error}


def validation_error_entry(repo: str, error: str) -> dict[str, str]:
    """Build an error entry for an invalid OWNER/REPO string.
    Input: repo -- raw invalid string. error -- description.
    Output: dict with repo and error keys.
    """
    return {"repo": repo, "error": error}
