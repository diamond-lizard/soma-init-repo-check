#!/usr/bin/env python3
"""Tests for OWNER/REPO string validation."""
from __future__ import annotations

from soma_init_repo_check.validation import validate_owner_repo


def test_valid_simple() -> None:
    """Valid alphanumeric OWNER/REPO passes validation."""
    assert validate_owner_repo("octocat/hello-world") is None


def test_valid_with_dots_underscores() -> None:
    """OWNER/REPO with dots and underscores passes validation."""
    assert validate_owner_repo("my.org/my_repo.js") is None


def test_valid_with_hyphens() -> None:
    """OWNER/REPO with hyphens passes validation."""
    assert validate_owner_repo("diamond-lizard/elpaca") is None


def test_missing_slash() -> None:
    """String without slash is rejected."""
    result = validate_owner_repo("noslash")
    assert result is not None
    assert "expected exactly one '/'" in result


def test_empty_owner() -> None:
    """Empty owner component is rejected."""
    result = validate_owner_repo("/repo")
    assert result is not None
    assert "owner is empty" in result


def test_empty_repo() -> None:
    """Empty repo component is rejected."""
    result = validate_owner_repo("owner/")
    assert result is not None
    assert "repo is empty" in result


def test_whitespace_in_owner() -> None:
    """Whitespace in owner is rejected."""
    result = validate_owner_repo("my owner/repo")
    assert result is not None
    assert "Invalid owner" in result


def test_path_separator_in_repo() -> None:
    """Path separator in repo is rejected (extra slash)."""
    result = validate_owner_repo("owner/repo/extra")
    assert result is not None
    assert "expected exactly one '/'" in result


def test_control_chars_in_repo() -> None:
    """Control characters in repo are rejected."""
    result = validate_owner_repo("owner/repo\x00name")
    assert result is not None
    assert "Invalid repo" in result


def test_empty_string() -> None:
    """Empty string is rejected."""
    result = validate_owner_repo("")
    assert result is not None


def test_only_slash() -> None:
    """Just a slash is rejected (both components empty)."""
    result = validate_owner_repo("/")
    assert result is not None
    assert "owner is empty" in result
