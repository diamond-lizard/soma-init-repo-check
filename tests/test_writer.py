#!/usr/bin/env python3
"""Tests for atomic file writing, stdout mode, and existence check."""
from __future__ import annotations

import json
import os
import stat

import pytest

from soma_init_repo_check.writer import write_atomic
from soma_init_repo_check.writer import write_output
from soma_init_repo_check.writer import write_stdout
from soma_init_repo_check.writer_check import check_output_exists


SAMPLE_DATA = {"results": [], "errors": []}


def test_atomic_write_creates_file(tmp_path: object) -> None:
    """Atomic write creates file with correct JSON content."""
    out = str(tmp_path) + "/output.json"
    write_atomic(out, SAMPLE_DATA)
    with open(out) as f:
        assert json.load(f) == SAMPLE_DATA


def test_atomic_write_removes_temp(tmp_path: object) -> None:
    """After atomic write, no .soma-tmp- files remain."""
    out = str(tmp_path) + "/output.json"
    write_atomic(out, SAMPLE_DATA)
    temps = [f for f in os.listdir(str(tmp_path)) if f.startswith(".soma-tmp-")]
    assert temps == []


def test_eexist_keeps_temp_and_exits(tmp_path: object) -> None:
    """EEXIST prints temp path to stderr and exits with code 1."""
    out = str(tmp_path) + "/output.json"
    with open(out, "w") as f:
        f.write("existing")
    with pytest.raises(SystemExit) as exc_info:
        write_atomic(out, SAMPLE_DATA)
    assert exc_info.value.code == 1
    temps = [f for f in os.listdir(str(tmp_path)) if f.startswith(".soma-tmp-")]
    assert len(temps) == 1
    with open(str(tmp_path) + "/" + temps[0]) as f:
        assert json.load(f) == SAMPLE_DATA


def test_stdout_mode(capsys: object) -> None:
    """Stdout mode writes JSON to stdout."""
    write_stdout(SAMPLE_DATA)
    captured = capsys.readouterr()
    assert json.loads(captured.out) == SAMPLE_DATA


def test_write_output_stdout(capsys: object) -> None:
    """write_output dispatches to stdout when path is '-'."""
    write_output("-", SAMPLE_DATA)
    captured = capsys.readouterr()
    assert json.loads(captured.out) == SAMPLE_DATA


def test_write_output_file(tmp_path: object) -> None:
    """write_output dispatches to atomic write for file paths."""
    out = str(tmp_path) + "/output.json"
    write_output(out, SAMPLE_DATA)
    with open(out) as f:
        assert json.load(f) == SAMPLE_DATA


def test_early_check_exits_if_exists(tmp_path: object) -> None:
    """Existence check exits with code 1 when file exists."""
    out = str(tmp_path) + "/output.json"
    with open(out, "w") as f:
        f.write("existing")
    with pytest.raises(SystemExit) as exc_info:
        check_output_exists(out)
    assert exc_info.value.code == 1


def test_early_check_skipped_for_stdout() -> None:
    """Existence check is skipped when OUTPUT_FILE is '-'."""
    check_output_exists("-")


def test_early_check_passes_for_missing(tmp_path: object) -> None:
    """Existence check passes when file does not exist."""
    check_output_exists(str(tmp_path) + "/nonexistent.json")


def test_output_permissions(tmp_path: object) -> None:
    """Output file permissions match umask-based value."""
    out = str(tmp_path) + "/output.json"
    write_atomic(out, SAMPLE_DATA)
    mask = os.umask(0)
    os.umask(mask)
    expected = 0o666 & ~mask
    actual = stat.S_IMODE(os.stat(out).st_mode)
    assert actual == expected
