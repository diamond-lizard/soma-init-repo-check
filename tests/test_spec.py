#!/usr/bin/env python3
"""Spec verification tests for soma-init-repo-check (Tests a, b, c)."""
from __future__ import annotations

from pathlib import Path

_TEST_EMACS_DIR = str(Path(__file__).parent / "data" / ".emacs.d")
_INITS_DIR = Path(__file__).parent / "data" / ".emacs.d" / "soma" / "inits"


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
