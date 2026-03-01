#!/usr/bin/env python3
"""Tests for session setup: cache path computation, headers, and config."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from unittest.mock import patch

import requests_cache

from soma_init_repo_check.auth import GitHubTokenAuth
from soma_init_repo_check.session import compute_cache_path, create_session


def test_cache_path_uses_xdg_when_set(tmp_path: Path) -> None:
    """Cache path uses $XDG_CACHE_HOME when set."""
    with patch.dict(os.environ, {"XDG_CACHE_HOME": str(tmp_path)}):
        result = compute_cache_path("/some/emacs/dir")
    assert result.parent.parent.parent == tmp_path
    assert "soma-init-repo-check" in str(result)
    assert "etags" in str(result)
    assert result.suffix == ".sqlite"


def test_cache_path_falls_back_to_dot_cache(tmp_path: Path) -> None:
    """Cache path falls back to ~/.cache when XDG_CACHE_HOME is unset."""
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(Path, "home", return_value=tmp_path):
            result = compute_cache_path("/some/emacs/dir")
    expected_base = tmp_path / ".cache" / "soma-init-repo-check" / "etags"
    assert result.parent == expected_base


def test_different_emacs_dirs_produce_different_hashes() -> None:
    """Different --emacs-dir values produce different hash components."""
    with patch.dict(os.environ, {"XDG_CACHE_HOME": "/tmp/cache"}):
        path1 = compute_cache_path("/home/user/.emacs.d")
        path2 = compute_cache_path("/home/other/.emacs.d")
    assert path1.stem != path2.stem


def test_cache_path_hash_is_first_16_hex_chars() -> None:
    """The hash component is the first 16 chars of the SHA-256 hex digest."""
    emacs_dir = "/home/user/.emacs.d"
    resolved = str(Path(emacs_dir).expanduser().resolve())
    expected = hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:16]
    with patch.dict(os.environ, {"XDG_CACHE_HOME": "/tmp/cache"}):
        result = compute_cache_path(emacs_dir)
    assert result.stem == expected


def test_create_session_has_correct_headers(tmp_path: Path) -> None:
    """The created session has the required GitHub API headers."""
    cache_path = tmp_path / "test_cache.sqlite"
    auth = GitHubTokenAuth("fake-token")
    session = create_session(cache_path, auth)
    assert session.headers["Accept"] == "application/vnd.github+json"
    assert session.headers["X-GitHub-Api-Version"] == "2022-11-28"
    assert session.headers["User-Agent"] == "soma-init-repo-check"


def test_create_session_has_auth(tmp_path: Path) -> None:
    """The created session has the auth instance attached."""
    cache_path = tmp_path / "test_cache.sqlite"
    auth = GitHubTokenAuth("fake-token")
    session = create_session(cache_path, auth)
    assert session.auth is auth


def test_create_session_has_expire_after_zero(tmp_path: Path) -> None:
    """The created session has expire_after=0 for forced revalidation."""
    cache_path = tmp_path / "test_cache.sqlite"
    auth = GitHubTokenAuth("fake-token")
    session = create_session(cache_path, auth)
    assert isinstance(session, requests_cache.CachedSession)
    assert session.settings.expire_after == 0
