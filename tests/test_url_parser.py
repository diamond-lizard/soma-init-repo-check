#!/usr/bin/env python3
"""Tests for URL parsing and host identification."""
from __future__ import annotations

from soma_init_repo_check.url_parser import derive_host_id, parse_repo_url


def test_parse_repo_url_github() -> None:
    """GitHub URL is identified as GitHub with correct OWNER/REPO."""
    owner, repo, host_id, is_github = parse_repo_url(
        "https://github.com/diamond-lizard/elpaca.git",
    )
    assert owner == "diamond-lizard"
    assert repo == "elpaca"
    assert host_id == "github"
    assert is_github is True


def test_parse_repo_url_non_github() -> None:
    """Non-GitHub URL uses derived host identifier."""
    owner, repo, host_id, is_github = parse_repo_url(
        "https://gitlab.com/user/project.git",
    )
    assert owner == "user"
    assert repo == "project"
    assert host_id == "gitlab"
    assert is_github is False


def test_derive_host_id_gitlab() -> None:
    """gitlab.com produces host id 'gitlab'."""
    assert derive_host_id("gitlab.com") == "gitlab"


def test_derive_host_id_codeberg() -> None:
    """codeberg.org produces host id 'codeberg'."""
    assert derive_host_id("codeberg.org") == "codeberg"


def test_derive_host_id_sr_ht() -> None:
    """sr.ht stays as full hostname (sr is only 2 chars)."""
    assert derive_host_id("sr.ht") == "sr.ht"


def test_parse_repo_url_github_case_insensitive() -> None:
    """GitHub hostname detection is case-insensitive."""
    _, _, host_id, is_github = parse_repo_url(
        "https://GitHub.COM/owner/repo",
    )
    assert host_id == "github"
    assert is_github is True
