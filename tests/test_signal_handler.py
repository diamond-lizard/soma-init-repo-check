#!/usr/bin/env python3
"""Tests for keyboard interrupt handler."""
from __future__ import annotations

import json
import os

import pytest

from soma_init_repo_check.signal_handler import handle_interrupt
from soma_init_repo_check.signal_handler import handle_pre_loop_interrupt


PARTIAL_RESULTS: list[dict[str, object]] = [
    {"status": "fork", "repo_url": "https://github.com/a/b",
     "ahead_by": 0, "behind_by": 3},
    {"status": "skipped:not_a_fork",
     "repo_url": "https://github.com/c/d"},
]
ERRORS: list[dict[str, str]] = [
    {"repo_url": "https://github.com/e/f", "error": "Not found"},
]


def test_writes_interrupted_json(tmp_path: object) -> None:
    """Handler writes JSON output with interrupted=true."""
    out = str(tmp_path) + "/out.json"
    with pytest.raises(SystemExit):
        handle_interrupt(out, PARTIAL_RESULTS, ERRORS, 5, quiet=True)
    with open(out) as f:
        data = json.load(f)
    assert data["interrupted"] is True
    assert len(data["results"]) == 2
    assert len(data["errors"]) == 1


def test_only_provided_results(tmp_path: object) -> None:
    """Only the N provided partial results appear in output."""
    out = str(tmp_path) + "/out.json"
    single = [PARTIAL_RESULTS[0]]
    with pytest.raises(SystemExit):
        handle_interrupt(out, single, [], 5, quiet=True)
    with open(out) as f:
        data = json.load(f)
    assert len(data["results"]) == 1
    assert data["results"][0]["repo_url"] == "https://github.com/a/b"


def test_summary_reflects_counts(tmp_path: object, capsys: object) -> None:
    """Summary on stderr reflects the partial result counts."""
    out = str(tmp_path) + "/out.json"
    with pytest.raises(SystemExit):
        handle_interrupt(out, PARTIAL_RESULTS, ERRORS, 5, quiet=False)
    err = capsys.readouterr().err
    assert "Forks: 1" in err
    assert "Errors: 1" in err
    assert "Entries in soma-inits: 5" in err


def test_exits_code_1(tmp_path: object) -> None:
    """Handler exits with code 1."""
    out = str(tmp_path) + "/out.json"
    with pytest.raises(SystemExit) as exc_info:
        handle_interrupt(out, PARTIAL_RESULTS, ERRORS, 5, quiet=True)
    assert exc_info.value.code == 1


def test_quiet_suppresses_summary(tmp_path: object, capsys: object) -> None:
    """Quiet suppresses summary but interrupt message still prints."""
    out = str(tmp_path) + "/out.json"
    with pytest.raises(SystemExit):
        handle_interrupt(out, PARTIAL_RESULTS, ERRORS, 5, quiet=True)
    err = capsys.readouterr().err
    assert "Forks:" not in err
    assert "Interrupted." in err


def test_stdout_mode(capsys: object) -> None:
    """Stdout mode writes JSON with interrupted=true to stdout."""
    with pytest.raises(SystemExit) as exc_info:
        handle_interrupt("-", PARTIAL_RESULTS, ERRORS, 5, quiet=True)
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["interrupted"] is True


def test_pre_loop_no_file(tmp_path: object, capsys: object) -> None:
    """Pre-loop interrupt: no output file created, exit code 1."""
    out = str(tmp_path) + "/out.json"
    with pytest.raises(SystemExit) as exc_info:
        handle_pre_loop_interrupt()
    assert exc_info.value.code == 1
    assert not os.path.exists(out)
    err = capsys.readouterr().err
    assert "Interrupted." in err
