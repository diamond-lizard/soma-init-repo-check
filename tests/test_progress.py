#!/usr/bin/env python3
"""Tests for progress message output."""
from __future__ import annotations

import io
from unittest.mock import patch

from soma_init_repo_check.progress import emit_checking
from soma_init_repo_check.progress import emit_skipping


def test_emit_checking_format() -> None:
    """emit_checking prints the expected format to stderr."""
    buf = io.StringIO()
    with patch("sys.stderr", buf):
        emit_checking(3, 10, "owner/repo")
    assert buf.getvalue() == "Checking repo 3/10: owner/repo...\n"


def test_emit_skipping_format() -> None:
    """emit_skipping prints the expected format to stderr."""
    buf = io.StringIO()
    with patch("sys.stderr", buf):
        emit_skipping(5, 10, "user/lib", "not on GitHub")
    assert buf.getvalue() == "Skipping repo 5/10: user/lib (not on GitHub)...\n"


def test_emit_checking_boundary() -> None:
    """Counter reaches TOTAL/TOTAL."""
    buf = io.StringIO()
    with patch("sys.stderr", buf):
        emit_checking(185, 185, "last/repo")
    assert "185/185" in buf.getvalue()
