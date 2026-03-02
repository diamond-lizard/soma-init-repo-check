#!/usr/bin/env python3
"""GitHub API endpoint functions for repo info and branch comparison."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import requests_cache
from urllib.parse import quote

from soma_init_repo_check.api_request import API_BASE
from soma_init_repo_check.api_request import request
from soma_init_repo_check.response import process_response


def fetch_repo_info(
    session: requests_cache.CachedSession, owner: str, repo: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Fetch repo info from GET /repos/{owner}/{repo}.

    URL-encodes path parameters. Uses rate limit retry.
    Extracts fork status, parent info, and default branches.

    Input: session -- CachedSession. owner, repo -- repo identifiers.
    Output: (info_dict, None) on success, (None, error) on failure.
    """
    url = f"{API_BASE}/repos/{quote(owner, safe='')}/{quote(repo, safe='')}"
    response = request(session, url)
    if response.status_code != 200:
        return None, f"HTTP {response.status_code} for {owner}/{repo}"
    data, err = process_response(response)
    if err:
        return None, err
    if not isinstance(data, dict):
        return None, f"Unexpected response for {owner}/{repo}"
    return _extract_repo_info(data, owner, repo)


def _extract_repo_info(
    data: dict[str, Any], owner: str, repo: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Extract fork status and parent info from parsed repo JSON.

    Input: data -- parsed JSON dict. owner, repo -- for error messages.
    Output: (info_dict, None) on success, (None, error) on failure.
    """
    if not data.get("fork", False):
        return {"fork": False}, None
    parent = data.get("parent")
    if not isinstance(parent, dict):
        return None, f"Fork {owner}/{repo} missing parent info"
    parts = parent.get("full_name", "").split("/", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None, f"Invalid parent full_name for {owner}/{repo}"
    return {
        "fork": True,
        "parent_owner": parts[0],
        "parent_repo": parts[1],
        "fork_default_branch": data.get("default_branch", ""),
        "parent_default_branch": parent.get("default_branch", ""),
    }, None


def fetch_compare(
    session: requests_cache.CachedSession, upstream_owner: str, upstream_repo: str,
    upstream_branch: str, fork_owner: str, fork_branch: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Compare branches via GET /repos/{up}/{repo}/compare/{base}...{head}.

    URL-encodes all path parameters. Extracts ahead_by and behind_by.

    Input: session -- CachedSession.
           upstream_owner, upstream_repo -- upstream parent repo.
           upstream_branch -- parent default branch.
           fork_owner, fork_branch -- fork owner and default branch.
    Output: (compare_dict, None) on success, (None, error) on failure.
    """
    base_spec = quote(upstream_branch, safe="")
    head_spec = quote(f"{fork_owner}:{fork_branch}", safe="")
    url = (
        f"{API_BASE}/repos/{quote(upstream_owner, safe='')}"
        f"/{quote(upstream_repo, safe='')}/compare/{base_spec}...{head_spec}"
    )
    response = request(session, url)
    if response.status_code != 200:
        return None, f"HTTP {response.status_code} comparing branches"
    data, err = process_response(response)
    if err:
        return None, err
    if not isinstance(data, dict):
        return None, "Unexpected compare response structure"
    ahead = data.get("ahead_by")
    behind = data.get("behind_by")
    if not isinstance(ahead, int) or not isinstance(behind, int):
        return None, "Missing ahead_by/behind_by in compare response"
    return {"ahead_by": ahead, "behind_by": behind}, None
