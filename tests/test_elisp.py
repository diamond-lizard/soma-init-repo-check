#!/usr/bin/env python3
"""Tests for Elisp comment stripping."""
from __future__ import annotations

from soma_init_repo_check.elisp import strip_comments


def test_full_line_comment_removed() -> None:
    """Full-line comments are removed entirely."""
    assert strip_comments("; this is a comment") == ""
    assert strip_comments("  ; indented comment") == ""
    assert strip_comments(";; double semicolon") == ""


def test_inline_comment_removed() -> None:
    """Inline comments are stripped from the end of a line."""
    assert strip_comments('(setq x 1) ; set x') == "(setq x 1)"


def test_semicolons_in_strings_preserved() -> None:
    """Semicolons inside double-quoted strings are not treated as comments."""
    result = strip_comments('(setq x "hello; world")')
    assert result == '(setq x "hello; world")'


def test_escaped_quotes_in_strings() -> None:
    """Escaped quotes inside strings do not end the string."""
    result = strip_comments(r'(setq x "say \"hi\"; ok")')
    assert result == r'(setq x "say \"hi\"; ok")'


def test_no_comments_passthrough() -> None:
    """Content with no comments passes through unchanged."""
    content = '(defun foo (x) (+ x 1))'
    assert strip_comments(content) == content


def test_empty_input() -> None:
    """Empty input returns empty output."""
    assert strip_comments("") == ""


def test_whitespace_before_semicolon_is_full_line() -> None:
    """Lines with only whitespace before ; are full-line comments."""
    assert strip_comments("   ; comment") == ""
    assert strip_comments("\t; tabbed comment") == ""


def test_multiline_mixed() -> None:
    """Multiple lines with mixed comments and code."""
    content = '; header comment\n(setq x 1) ; inline\n(setq y "a;b")'
    result = strip_comments(content)
    assert result == '\n(setq x 1)\n(setq y "a;b")'
