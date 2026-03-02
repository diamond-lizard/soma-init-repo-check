#!/usr/bin/env python3
"""End-to-end integration tests for soma-init-repo-check."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from click.testing import CliRunner

from soma_init_repo_check.cli import main

_TEST_EMACS_DIR = str(Path(__file__).parent / "data" / ".emacs.d")


def _pass_available() -> bool:
    """Check whether pass and the token entry are available."""
    try:
        result = subprocess.run(
            ["pass", "github.com/fgpat/public-repos-only"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


_skip_no_pass = pytest.mark.skipif(
    not _pass_available(),
    reason="pass entry not available",
)


def _run_full(tmp_path: Path) -> dict:
    """Run the full pipeline and return parsed JSON output."""
    outfile = tmp_path / "output.json"
    runner = CliRunner()
    result = runner.invoke(main, [
        str(outfile), "--emacs-dir", _TEST_EMACS_DIR,
    ])
    assert result.exit_code == 0, result.output
    return json.loads(outfile.read_text())


@_skip_no_pass
def test_full_run_json_structure(tmp_path: Path) -> None:
    """Full run produces valid JSON with results and errors keys."""
    data = _run_full(tmp_path)
    assert "results" in data
    assert "errors" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["errors"], list)
    assert "interrupted" not in data


@_skip_no_pass
def test_full_run_results_sorted(tmp_path: Path) -> None:
    """Results array is sorted by init file then OWNER/REPO."""
    data = _run_full(tmp_path)
    results = data["results"]
    keys = []
    for r in results:
        if "repo_url" in r:
            keys.append(r["repo_url"])
        elif "init_file" in r:
            keys.append(r["init_file"])
        elif "repo" in r:
            keys.append(r["repo"])
    assert keys == sorted(keys)


@_skip_no_pass
def test_full_run_fork_entries_have_integers(tmp_path: Path) -> None:
    """Fork entries have ahead_by and behind_by as integers."""
    data = _run_full(tmp_path)
    forks = [r for r in data["results"] if r.get("status") == "fork"]
    for f in forks:
        assert isinstance(f["ahead_by"], int)
        assert isinstance(f["behind_by"], int)
        assert "repo_url" in f


@_skip_no_pass
def test_full_run_skipped_entries_have_valid_status(tmp_path: Path) -> None:
    """Skipped entries have expected status values."""
    data = _run_full(tmp_path)
    valid_statuses = {
        "fork", "skipped:not_a_fork",
        "skipped:not_github", "skipped:no_repo_directive",
        "skipped:no_host",
    }
    for r in data["results"]:
        assert r["status"] in valid_statuses
