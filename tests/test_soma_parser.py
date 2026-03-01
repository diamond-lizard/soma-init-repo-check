#!/usr/bin/env python3
"""Tests for soma init file discovery, reading, and repo extraction."""
from __future__ import annotations

from pathlib import Path

from soma_init_repo_check.soma_parser import resolve_init_paths
from soma_init_repo_check.soma_reader import read_init_file
from soma_init_repo_check.soma_extractor import extract_repos

_TEST_EMACS_DIR = str(Path(__file__).parent / "data" / ".emacs.d")
_INITS_DIR = Path(__file__).parent / "data" / ".emacs.d" / "soma" / "inits"


def test_resolve_finds_rainbow_mode_init() -> None:
    """File discovery finds soma-rainbow-mode-init.el in inits dir."""
    valid, errors = resolve_init_paths(
        ["soma-rainbow-mode-init"], _TEST_EMACS_DIR,
    )
    assert len(valid) == 1
    assert valid[0][0] == "soma-rainbow-mode-init"
    assert valid[0][1].name == "soma-rainbow-mode-init.el"
    assert len(errors) == 0


def test_extract_rainbow_mode_repo() -> None:
    """Repo extraction yields emacs-packages/rainbow-mode as GitHub."""
    path = _INITS_DIR / "soma-rainbow-mode-init.el"
    tree, err = read_init_file(path)
    assert tree is not None
    assert err is None
    repos, skipped = extract_repos(tree, "soma-rainbow-mode-init.el")
    assert len(repos) == 1
    assert repos[0]["owner"] == "emacs-packages"
    assert repos[0]["repo"] == "rainbow-mode"
    assert repos[0]["host"] == "github"
    assert repos[0]["init_file"] == "soma-rainbow-mode-init.el"


def test_path_traversal_dotdot_rejected(tmp_path: Path) -> None:
    """Symbol with .. components is rejected as path traversal."""
    inits = tmp_path / "soma" / "inits"
    inits.mkdir(parents=True)
    valid, errors = resolve_init_paths(["../../../etc/passwd"], str(tmp_path))
    assert len(valid) == 0
    assert len(errors) == 1
    assert "Path traversal" in errors[0]["error"]


def test_path_traversal_symlink_rejected(tmp_path: Path) -> None:
    """Symlink pointing outside inits directory is rejected."""
    inits = tmp_path / "soma" / "inits"
    inits.mkdir(parents=True)
    outside = tmp_path / "outside.el"
    outside.write_text("(provide 'outside)")
    link = inits / "evil-init.el"
    link.symlink_to(outside)
    valid, errors = resolve_init_paths(["evil-init"], str(tmp_path))
    assert len(valid) == 0
    assert len(errors) == 1
    assert "Path traversal" in errors[0]["error"]


def test_no_repo_directive_produces_skip() -> None:
    """Init file with no :repo yields skipped:no_repo_directive."""
    import sexpdata
    tree = sexpdata.parse("(use-package foo :commands bar)")
    repos, skipped = extract_repos(tree, "soma-foo-init.el")
    assert len(repos) == 0
    assert len(skipped) == 1
    assert skipped[0]["status"] == "skipped:no_repo_directive"
    assert skipped[0]["init_file"] == "soma-foo-init.el"


def test_no_host_produces_skip() -> None:
    """Init file with :repo but no :host yields skipped:no_host."""
    import sexpdata
    content = '(use-package foo :ensure (:repo "owner/name"))'
    tree = sexpdata.parse(content)
    repos, skipped = extract_repos(tree, "soma-foo-init.el")
    assert len(repos) == 0
    assert len(skipped) == 1
    assert skipped[0]["status"] == "skipped:no_host"
    assert skipped[0]["repo"] == "owner/name"


def test_host_gitlab_produces_not_github() -> None:
    """Init file with :host gitlab yields skipped:not_github."""
    import sexpdata
    content = '(use-package foo :ensure (:host gitlab :repo "o/r"))'
    tree = sexpdata.parse(content)
    repos, skipped = extract_repos(tree, "soma-foo-init.el")
    assert len(repos) == 0
    assert len(skipped) == 1
    assert skipped[0]["status"] == "skipped:not_github"
    assert skipped[0]["host"] == "gitlab"


def test_missing_file_produces_error() -> None:
    """Missing init file is recorded in errors."""
    path = Path("/nonexistent/soma-foo-init.el")
    tree, err = read_init_file(path)
    assert tree is None
    assert err is not None
    assert "File not found" in err["error"]
    assert err["init_file"] == "soma-foo-init.el"


def test_oversized_file_produces_error(tmp_path: Path) -> None:
    """Init file > 1 MB is recorded in errors."""
    big = tmp_path / "soma-big-init.el"
    big.write_text("x" * 1_100_000)
    tree, err = read_init_file(big)
    assert tree is None
    assert err is not None
    assert "exceeds 1 MB" in err["error"]


def test_parse_failure_produces_error(tmp_path: Path) -> None:
    """Unparseable init file is recorded in errors."""
    bad = tmp_path / "soma-bad-init.el"
    bad.write_text("((( malformed")
    tree, err = read_init_file(bad)
    assert tree is None
    assert err is not None
    assert "Parse error" in err["error"]
