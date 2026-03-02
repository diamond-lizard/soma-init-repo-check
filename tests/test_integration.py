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
_INITS_DIR = Path(__file__).parent / "data" / ".emacs.d" / "soma" / "inits"


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


@_skip_no_pass
def test_full_run_json_structure(tmp_path: Path) -> None:
    """Full run produces valid JSON with results and errors keys."""
    outfile = tmp_path / "output.json"
    runner = CliRunner()
    result = runner.invoke(main, [
        str(outfile), "--emacs-dir", _TEST_EMACS_DIR,
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(outfile.read_text())
    assert "results" in data
    assert "errors" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["errors"], list)
    assert "interrupted" not in data


@_skip_no_pass
def test_full_run_results_sorted(tmp_path: Path) -> None:
    """Results array is sorted by init file then OWNER/REPO."""
    outfile = tmp_path / "output.json"
    runner = CliRunner()
    result = runner.invoke(main, [
        str(outfile), "--emacs-dir", _TEST_EMACS_DIR,
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(outfile.read_text())
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
    outfile = tmp_path / "output.json"
    runner = CliRunner()
    result = runner.invoke(main, [
        str(outfile), "--emacs-dir", _TEST_EMACS_DIR,
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(outfile.read_text())
    forks = [r for r in data["results"] if r.get("status") == "fork"]
    for f in forks:
        assert isinstance(f["ahead_by"], int)
        assert isinstance(f["behind_by"], int)
        assert "repo_url" in f


@_skip_no_pass
def test_full_run_skipped_entries_have_valid_status(tmp_path: Path) -> None:
    """Skipped entries have expected status values."""
    outfile = tmp_path / "output.json"
    runner = CliRunner()
    result = runner.invoke(main, [
        str(outfile), "--emacs-dir", _TEST_EMACS_DIR,
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(outfile.read_text())
    valid_statuses = {
        "fork", "skipped:not_a_fork",
        "skipped:not_github", "skipped:no_repo_directive",
        "skipped:no_host",
    }
    for r in data["results"]:
        assert r["status"] in valid_statuses


def test_soma_inits_extraction_and_file_existence() -> None:
    """Soma-inits extraction succeeds; only rainbow-mode exists on disk."""
    from soma_init_repo_check.init_parser import (
        extract_soma_inits, read_init_el,
    )
    tree = read_init_el(_TEST_EMACS_DIR)
    inits = extract_soma_inits(tree)
    assert len(inits) > 0
    existing = [
        s for s in inits
        if (_INITS_DIR / f"{s}.el").exists()
    ]
    assert existing == ["soma-rainbow-mode-init"]


def test_elpaca_bootstrap_repo_extracted() -> None:
    """Elpaca bootstrap repo is diamond-lizard/elpaca (spec Test b)."""
    from soma_init_repo_check.init_parser import (
        extract_elpaca_repo_url, read_init_el,
    )
    from soma_init_repo_check.url_parser import parse_repo_url
    tree = read_init_el(_TEST_EMACS_DIR)
    url = extract_elpaca_repo_url(tree)
    owner, repo, host_id, is_github = parse_repo_url(url)
    assert owner == "diamond-lizard"
    assert repo == "elpaca"
    assert is_github is True
    assert host_id == "github"


def test_rainbow_mode_repo_extracted() -> None:
    """rainbow-mode repo is emacs-packages/rainbow-mode (spec Test c)."""
    from soma_init_repo_check.soma_extractor import extract_repos
    from soma_init_repo_check.soma_reader import read_init_file
    path = _INITS_DIR / "soma-rainbow-mode-init.el"
    tree, err = read_init_file(path)
    assert tree is not None
    assert err is None
    repos, skipped = extract_repos(tree, "soma-rainbow-mode-init.el")
    assert len(repos) == 1
    assert repos[0]["owner"] == "emacs-packages"
    assert repos[0]["repo"] == "rainbow-mode"
    assert repos[0]["host"] == "github"
