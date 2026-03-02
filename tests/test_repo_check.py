#!/usr/bin/env python3
"""Tests for repo check orchestration logic."""
from __future__ import annotations

from typing import Any
from unittest.mock import patch

from soma_init_repo_check.repo_check import check_repo


_FORK_INFO = {
    "fork": True,
    "parent_owner": "upstream",
    "parent_repo": "repo",
    "fork_default_branch": "main",
    "parent_default_branch": "main",
}


@patch("soma_init_repo_check.repo_check.fetch_compare")
@patch("soma_init_repo_check.repo_check.fetch_repo_info")
def test_fork_info_ok_compare_fails_goes_to_errors(
    mock_info: Any, mock_compare: Any,
) -> None:
    """Fork identified but compare fails: result in errors, not results."""
    mock_info.return_value = (_FORK_INFO, None)
    mock_compare.return_value = (None, "HTTP 500 comparing branches")
    result, error = check_repo(None, "owner", "repo")
    assert result is None
    assert error is not None
    assert "repo_url" in error
    assert "500" in error["error"]


@patch("soma_init_repo_check.repo_check.fetch_compare")
@patch("soma_init_repo_check.repo_check.fetch_repo_info")
def test_fork_info_ok_compare_ok_produces_result(
    mock_info: Any, mock_compare: Any,
) -> None:
    """Fork identified and compare succeeds: produces a fork result."""
    mock_info.return_value = (_FORK_INFO, None)
    mock_compare.return_value = ({"ahead_by": 0, "behind_by": 3}, None)
    result, error = check_repo(None, "owner", "repo")
    assert error is None
    assert result is not None
    assert result["status"] == "fork"
    assert result["behind_by"] == 3


@patch("soma_init_repo_check.repo_check.fetch_repo_info")
def test_repo_info_fails_goes_to_errors(mock_info: Any) -> None:
    """Repo info API failure records in errors."""
    mock_info.return_value = (None, "HTTP 404 for owner/repo")
    result, error = check_repo(None, "owner", "repo")
    assert result is None
    assert error is not None
    assert "404" in error["error"]


@patch("soma_init_repo_check.repo_check.fetch_repo_info")
def test_not_a_fork_produces_skipped_result(mock_info: Any) -> None:
    """Non-fork repo produces skipped:not_a_fork result."""
    mock_info.return_value = ({"fork": False}, None)
    result, error = check_repo(None, "owner", "repo")
    assert error is None
    assert result is not None
    assert result["status"] == "skipped:not_a_fork"
