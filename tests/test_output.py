#!/usr/bin/env python3
"""Tests for output formatting, entry construction, sorting, and assembly."""
from __future__ import annotations

from soma_init_repo_check.output import api_error_entry
from soma_init_repo_check.output import fork_entry
from soma_init_repo_check.output import init_file_error_entry
from soma_init_repo_check.output import no_host_entry
from soma_init_repo_check.output import no_repo_entry
from soma_init_repo_check.output import not_a_fork_entry
from soma_init_repo_check.output import not_github_entry
from soma_init_repo_check.output import validation_error_entry


def test_fork_entry_structure() -> None:
    """Fork entry has status, repo_url, ahead_by, behind_by."""
    e = fork_entry("owner", "repo", 2, 5)
    assert e["status"] == "fork"
    assert e["repo_url"] == "https://github.com/owner/repo"
    assert e["ahead_by"] == 2
    assert e["behind_by"] == 5


def test_not_a_fork_entry_structure() -> None:
    """Not-a-fork entry has status and repo_url."""
    e = not_a_fork_entry("owner", "repo")
    assert e["status"] == "skipped:not_a_fork"
    assert e["repo_url"] == "https://github.com/owner/repo"


def test_not_github_entry_structure() -> None:
    """Not-github entry has status, repo, host (no repo_url)."""
    e = not_github_entry("user/proj", "gitlab", "soma-foo-init.el")
    assert e["status"] == "skipped:not_github"
    assert e["repo"] == "user/proj"
    assert e["host"] == "gitlab"


def test_no_repo_entry_structure() -> None:
    """No-repo entry has status and init_file."""
    e = no_repo_entry("soma-foo-init.el")
    assert e["status"] == "skipped:no_repo_directive"
    assert e["init_file"] == "soma-foo-init.el"


def test_no_host_entry_structure() -> None:
    """No-host entry has status, init_file, and repo."""
    e = no_host_entry("soma-bar-init.el", "user/bar")
    assert e["status"] == "skipped:no_host"
    assert e["init_file"] == "soma-bar-init.el"
    assert e["repo"] == "user/bar"


def test_api_error_entry_structure() -> None:
    """API error has repo_url and error."""
    e = api_error_entry("https://github.com/o/r", "HTTP 500")
    assert e["repo_url"] == "https://github.com/o/r"
    assert e["error"] == "HTTP 500"


def test_init_file_error_entry_structure() -> None:
    """Init file error has init_file and error."""
    e = init_file_error_entry("soma-x-init.el", "File not found")
    assert e["init_file"] == "soma-x-init.el"
    assert e["error"] == "File not found"


def test_validation_error_entry_structure() -> None:
    """Validation error has repo and error."""
    e = validation_error_entry("bad//repo", "Invalid OWNER/REPO")
    assert e["repo"] == "bad//repo"
    assert e["error"] == "Invalid OWNER/REPO"

