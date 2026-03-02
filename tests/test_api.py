#!/usr/bin/env python3
"""Tests for GitHub API endpoints using real API calls."""
from __future__ import annotations

import subprocess

import pytest

from soma_init_repo_check.api import fetch_compare
from soma_init_repo_check.api import fetch_repo_info
from soma_init_repo_check.auth import GitHubTokenAuth
from soma_init_repo_check.session import compute_cache_path
from soma_init_repo_check.session import create_session


def _get_session():
    """Create a real CachedSession with token from pass."""
    try:
        result = subprocess.run(
            ["pass", "github.com/fgpat/public-repos-only"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            pytest.skip("pass entry not available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("pass not available")
    token = result.stdout.split("\n", 1)[0].strip()
    if not token:
        pytest.skip("empty token from pass")
    auth = GitHubTokenAuth(token)
    cache_path = compute_cache_path("/tmp/test-emacs-dir")
    return create_session(cache_path, auth)


def test_fetch_repo_info_fork() -> None:
    """Fetch info for a known fork and verify fork fields."""
    session = _get_session()
    info, err = fetch_repo_info(session, "diamond-lizard", "elpaca")
    assert err is None
    assert info is not None
    assert info["fork"] is True
    assert "parent_owner" in info
    assert "parent_repo" in info
    assert "fork_default_branch" in info
    assert "parent_default_branch" in info


def test_fetch_repo_info_not_fork() -> None:
    """Fetch info for a known non-fork repo."""
    session = _get_session()
    info, err = fetch_repo_info(session, "progfolio", "elpaca")
    assert err is None
    assert info is not None
    assert info["fork"] is False


def test_fetch_compare_on_fork() -> None:
    """Compare branches on a known fork and verify ahead/behind."""
    session = _get_session()
    info, err = fetch_repo_info(session, "diamond-lizard", "elpaca")
    assert err is None and info is not None and info["fork"] is True
    cmp, cmp_err = fetch_compare(
        session,
        info["parent_owner"], info["parent_repo"],
        info["parent_default_branch"],
        "diamond-lizard", info["fork_default_branch"],
    )
    assert cmp_err is None
    assert cmp is not None
    assert isinstance(cmp["ahead_by"], int)
    assert isinstance(cmp["behind_by"], int)
