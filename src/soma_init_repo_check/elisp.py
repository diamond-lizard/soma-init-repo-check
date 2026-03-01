#!/usr/bin/env python3
"""Strip Elisp comments from source content.

Handles full-line comments, inline comments, and preserves
semicolons inside double-quoted string literals.
"""
from __future__ import annotations


def strip_comments(content: str) -> str:
    """Remove Elisp comments from source content.

    Full-line comments (first non-whitespace is ;) are removed entirely.
    Inline comments (unquoted ; to end of line) are stripped.
    Semicolons inside double-quoted strings are preserved.
    Escaped quotes inside strings are handled correctly.

    Input: Elisp source content as a string.
    Output: Content with all comments removed.
    """
    lines = content.split("\n")
    result = [_strip_line(line) for line in lines]
    return "\n".join(result)


def _strip_line(line: str) -> str:
    """Strip comment from a single line of Elisp source.

    Input: a single line of Elisp (no newline).
    Output: the line with any comment removed, or empty if full-line comment.
    """
    if _is_full_line_comment(line):
        return ""
    return _remove_inline_comment(line)


def _is_full_line_comment(line: str) -> bool:
    """Return True if the line is a full-line comment.

    A full-line comment has ; as its first non-whitespace character.

    Input: a single line of Elisp.
    Output: True if the line is a full-line comment.
    """
    stripped = line.lstrip()
    return stripped.startswith(";")


def _remove_inline_comment(line: str) -> str:
    """Remove an inline comment from a line, preserving string contents.

    Walks the line character by character, tracking whether we are
    inside a double-quoted string. Semicolons inside strings are kept.
    Escaped quotes inside strings do not toggle the in-string state.

    Input: a single line of Elisp (not a full-line comment).
    Output: the line with any inline comment removed.
    """
    pos = _find_comment_start(line)
    if pos == -1:
        return line
    return line[:pos].rstrip()


def _find_comment_start(line: str) -> int:
    """Find the position of the first unquoted semicolon in a line.

    Tracks string state to skip semicolons inside double-quoted strings.
    Handles escaped quotes (backslash-quote) inside strings.

    Input: a single line of Elisp.
    Output: index of the comment-starting semicolon, or -1 if none.
    """
    in_string = False
    i = 0
    while i < len(line):
        ch = line[i]
        if in_string:
            if ch == "\\" and i + 1 < len(line):
                i += 2
                continue
            if ch == '"':
                in_string = False
        else:
            if ch == ";":
                return i
            if ch == '"':
                in_string = True
        i += 1
    return -1
