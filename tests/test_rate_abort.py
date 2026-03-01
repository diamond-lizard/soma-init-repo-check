#!/usr/bin/env python3
"""Tests for rate limit abort behavior."""
from __future__ import annotations

import json
import os

import pytest

from soma_init_repo_check.rate_abort import abort_rate_limit
from soma_init_repo_check.rate_abort import build_abort_message


def test_abort_message_with_file_path() -> None:
    """Abort message includes the output file path."""
    msg = build_abort_message("/tmp/output.json")
    assert "/tmp/output.json" in msg
    assert "rate limit" in msg.lower()


def test_abort_message_with_stdout() -> None:
    """Abort message says stdout when output is -."""
    msg = build_abort_message("-")
    assert "stdout" in msg


def test_abort_writes_partial_results_to_file(tmp_path: object) -> None:
    """Abort writes JSON with interrupted=true to the output file."""
    assert isinstance(tmp_path, os.PathLike)
    out = str(tmp_path / "partial.json")
    results = [{"status": "fork", "repo_url": "https://github.com/a/b"}]
    errors = [{"repo_url": "https://github.com/c/d", "error": "fail"}]
    with pytest.raises(SystemExit) as exc_info:
        abort_rate_limit(out, results, errors, quiet=False)
    assert exc_info.value.code == 1
    with open(out, encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["interrupted"] is True
    assert len(data["results"]) == 1
    assert len(data["errors"]) == 1


def test_abort_writes_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """Abort writes JSON to stdout when output is -."""
    with pytest.raises(SystemExit) as exc_info:
        abort_rate_limit("-", [], [], quiet=True)
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["interrupted"] is True


def test_abort_prints_message_to_stderr(
    tmp_path: object,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Abort prints descriptive message to stderr unless quiet."""
    assert isinstance(tmp_path, os.PathLike)
    out = str(tmp_path / "partial.json")
    with pytest.raises(SystemExit):
        abort_rate_limit(out, [], [], quiet=False)
    captured = capsys.readouterr()
    assert "rate limit" in captured.err.lower()


def test_abort_quiet_suppresses_stderr(
    tmp_path: object,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Abort with quiet=True suppresses stderr output."""
    assert isinstance(tmp_path, os.PathLike)
    out = str(tmp_path / "partial.json")
    with pytest.raises(SystemExit):
        abort_rate_limit(out, [], [], quiet=True)
    captured = capsys.readouterr()
    assert captured.err == ""
