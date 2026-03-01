#!/usr/bin/env python3
"""Tests for init.el parsing."""
from __future__ import annotations

from pathlib import Path

from soma_init_repo_check.init_parser import (
    extract_elpaca_repo_url,
    extract_soma_inits,
    read_init_el,
)

_TEST_EMACS_DIR = str(Path(__file__).parent / "data" / ".emacs.d")


def test_read_init_el_returns_parsed_tree() -> None:
    """read_init_el returns a non-empty list of s-expressions."""
    tree = read_init_el(_TEST_EMACS_DIR)
    assert isinstance(tree, list)
    assert len(tree) > 0


def test_extract_elpaca_repo_url() -> None:
    """Elpaca bootstrap repo URL is extracted as diamond-lizard/elpaca."""
    tree = read_init_el(_TEST_EMACS_DIR)
    url = extract_elpaca_repo_url(tree)
    assert url == "https://github.com/diamond-lizard/elpaca.git"


def test_extract_soma_inits_count() -> None:
    """soma-inits list contains approximately 210 symbols."""
    tree = read_init_el(_TEST_EMACS_DIR)
    inits = extract_soma_inits(tree)
    assert isinstance(inits, list)
    assert len(inits) > 200
    assert len(inits) < 220


def test_extract_soma_inits_contains_known_symbols() -> None:
    """soma-inits list contains known symbol names."""
    tree = read_init_el(_TEST_EMACS_DIR)
    inits = extract_soma_inits(tree)
    assert "soma-magit-init" in inits
    assert "soma-dash-init" in inits
    assert "soma-evil-init" in inits


def test_missing_init_el_exits(tmp_path: Path, capsys) -> None:
    """Missing init.el prints error with path and exits with code 1."""
    import pytest
    with pytest.raises(SystemExit) as exc_info:
        read_init_el(str(tmp_path))
    assert exc_info.value.code == 1
    assert "init.el not found" in capsys.readouterr().err


def test_missing_elpaca_order_exits(capsys) -> None:
    """Missing elpaca-order in tree exits with error."""
    import pytest
    with pytest.raises(SystemExit) as exc_info:
        extract_elpaca_repo_url([])
    assert exc_info.value.code == 1
    assert "elpaca-order not found" in capsys.readouterr().err


def test_missing_soma_inits_exits(capsys) -> None:
    """Missing soma-inits in tree exits with error."""
    import pytest
    with pytest.raises(SystemExit) as exc_info:
        extract_soma_inits([])
    assert exc_info.value.code == 1
    assert "soma-inits not found" in capsys.readouterr().err


def test_oversized_init_el_exits(tmp_path: Path, capsys) -> None:
    """init.el exceeding 1 MB exits with error."""
    import pytest
    init_el = tmp_path / "init.el"
    init_el.write_text("x" * 1_100_000)
    with pytest.raises(SystemExit) as exc_info:
        read_init_el(str(tmp_path))
    assert exc_info.value.code == 1
    assert "exceeds 1 MB" in capsys.readouterr().err


def test_sexpdata_parse_failure_exits(tmp_path: Path, capsys) -> None:
    """Unparseable init.el exits with descriptive error."""
    import pytest
    init_el = tmp_path / "init.el"
    init_el.write_text("((( malformed")
    with pytest.raises(SystemExit) as exc_info:
        read_init_el(str(tmp_path))
    assert exc_info.value.code == 1
    assert "failed to parse" in capsys.readouterr().err
