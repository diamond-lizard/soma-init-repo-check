#!/usr/bin/env python3
"""TypedDict definitions for GitHub API response structures."""
from __future__ import annotations

from typing import TypedDict


class _RepoInfoRequired(TypedDict):
    """Required fields in a repo info API response."""

    fork: bool


class RepoInfoResponse(_RepoInfoRequired, total=False):
    """Processed repo info from the GitHub API.

    The fork field is always present. The remaining fields are
    only present when fork is True.
    """

    parent_owner: str
    parent_repo: str
    fork_default_branch: str
    parent_default_branch: str


class CompareResponse(TypedDict):
    """Processed branch comparison from the GitHub API."""

    ahead_by: int
    behind_by: int


def str_field(data: dict[str, object], key: str) -> str:
    """Get a string field from a JSON dict, defaulting to empty.

    Input: data -- parsed JSON dict. key -- field name.
    Output: the string value, or '' if missing or not a string.
    """
    val = data.get(key, "")
    return val if isinstance(val, str) else ""
