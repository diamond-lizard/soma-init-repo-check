#!/usr/bin/env python3
"""Tests for output sorting and assembly logic."""
from __future__ import annotations

from soma_init_repo_check.output_assembly import assemble_output
from soma_init_repo_check.output_sort import sort_errors
from soma_init_repo_check.output_sort import sort_results


def test_sort_results_by_init_file() -> None:
    """Results sort by init file name (primary key)."""
    r = [
        {"init_file": "soma-z-init.el", "status": "skipped:no_repo_directive"},
        {"repo_url": "https://github.com/a/b", "status": "fork", "init_file": "soma-a-init.el"},
        {"init_file": "soma-m-init.el", "status": "skipped:no_repo_directive"},
    ]
    s = sort_results(r)
    files = [e.get("init_file", "init.el") for e in s]
    assert files == ["soma-a-init.el", "soma-m-init.el", "soma-z-init.el"]


def test_sort_within_same_init_file() -> None:
    """Within same init file, sort by OWNER/REPO."""
    r = [
        {"repo_url": "https://github.com/z/repo", "status": "fork", "init_file": "f.el"},
        {"repo_url": "https://github.com/a/repo", "status": "fork", "init_file": "f.el"},
    ]
    s = sort_results(r)
    assert "a/repo" in s[0]["repo_url"]
    assert "z/repo" in s[1]["repo_url"]


def test_elpaca_sorts_under_init_el() -> None:
    """Elpaca bootstrap repo (no init_file) sorts under init.el."""
    r = [
        {"init_file": "soma-z-init.el", "status": "skipped:no_repo_directive"},
        {"repo_url": "https://github.com/user/elpaca", "status": "fork"},
    ]
    s = sort_results(r)
    assert s[0]["repo_url"] == "https://github.com/user/elpaca"
    assert s[1].get("init_file") == "soma-z-init.el"


def test_sort_errors_by_init_file() -> None:
    """Errors sort by init file, then identifier."""
    errs = [
        {"repo_url": "https://github.com/z/r", "error": "fail"},
        {"init_file": "soma-a-init.el", "error": "File not found"},
    ]
    s = sort_errors(errs)
    assert "init_file" not in s[0]
    assert s[1]["init_file"] == "soma-a-init.el"


def test_assemble_output_normal() -> None:
    """Assembly produces sorted results/errors, no interrupted key."""
    results = [{"repo_url": "https://github.com/a/b", "status": "fork"}]
    errors = [{"repo_url": "https://github.com/x/y", "error": "fail"}]
    out = assemble_output(results, errors)
    assert "results" in out
    assert "errors" in out
    assert "interrupted" not in out


def test_assemble_output_interrupted() -> None:
    """When interrupted, 'interrupted': true is present."""
    out = assemble_output([], [], interrupted=True)
    assert out["interrupted"] is True


def test_assemble_output_not_interrupted_omits_key() -> None:
    """When not interrupted, 'interrupted' key is absent."""
    out = assemble_output([], [])
    assert "interrupted" not in out
