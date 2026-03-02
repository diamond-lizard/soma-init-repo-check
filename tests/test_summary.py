#!/usr/bin/env python3
"""Tests for summary counter computation and output."""
from __future__ import annotations

import io
from typing import Any
from unittest.mock import patch

from soma_init_repo_check.summary import compute_summary
from soma_init_repo_check.summary import print_summary


def _sample_results() -> list[dict[str, Any]]:
    """Build a representative set of result entries."""
    return [
        {"status": "fork", "repo_url": "https://github.com/a/b",
         "ahead_by": 0, "behind_by": 3},
        {"status": "fork", "repo_url": "https://github.com/c/d",
         "ahead_by": 1, "behind_by": 0},
        {"status": "skipped:not_a_fork", "repo_url": "https://github.com/e/f"},
        {"status": "skipped:not_github", "repo": "x/y", "host": "gitlab"},
        {"status": "skipped:not_github", "repo": "z/w", "host": "codeberg"},
        {"status": "skipped:no_repo_directive", "init_file": "soma-foo-init.el"},
        {"status": "skipped:no_host", "init_file": "soma-bar-init.el", "repo": "m/n"},
        {"status": "skipped:no_host", "init_file": "soma-bar-init.el", "repo": "p/q"},
        {"status": "skipped:no_host", "init_file": "soma-baz-init.el", "repo": "r/s"},
    ]


def _sample_errors() -> list[dict[str, str]]:
    """Build a representative set of error entries."""
    return [
        {"repo_url": "https://github.com/err/one", "error": "404"},
        {"repo_url": "https://github.com/err/two", "error": "timeout"},
        {"init_file": "soma-bad-init.el", "error": "File not found"},
        {"repo": "inv@lid/repo!", "error": "Invalid OWNER/REPO"},
    ]


def test_compute_summary_counters() -> None:
    """Verify each counter is correct for a known data set."""
    c = compute_summary(210, _sample_results(), _sample_errors())
    assert c["init_count"] == 210
    assert c["no_repo"] == 1
    assert c["no_host"] == 2
    assert c["init_errors"] == 1
    assert c["forks"] == 2
    assert c["behind"] == 1
    assert c["skipped"] == 2
    assert c["validation_errors"] == 1
    assert c["errors"] == 2
    assert c["checked"] == 2 + 1 + 2


def test_summary_relationship_unique() -> None:
    """Unique repos = Repos checked + Skipped + Validation errors."""
    c = compute_summary(100, _sample_results(), _sample_errors())
    assert c["unique"] == c["checked"] + c["skipped"] + c["validation_errors"]


def test_summary_relationship_checked() -> None:
    """Repos checked = Forks + not-a-fork + Errors."""
    results = _sample_results()
    naf = sum(1 for r in results if r.get("status") == "skipped:not_a_fork")
    c = compute_summary(100, results, _sample_errors())
    assert c["checked"] == c["forks"] + naf + c["errors"]


def test_summary_empty_inputs() -> None:
    """Empty results and errors produce all-zero counters."""
    c = compute_summary(0, [], [])
    assert c["unique"] == 0
    assert c["checked"] == 0
    assert c["unique"] == c["checked"] + c["skipped"] + c["validation_errors"]


def test_print_summary_output() -> None:
    """print_summary writes expected lines to stderr."""
    c = compute_summary(5, _sample_results(), _sample_errors())
    buf = io.StringIO()
    with patch("sys.stderr", buf):
        print_summary(c)
    output = buf.getvalue()
    assert "Entries in soma-inits: 5" in output
    assert "Forks: 2" in output
    assert "Behind upstream: 1" in output
    assert "Errors: 2" in output
