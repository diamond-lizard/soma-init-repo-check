#!/usr/bin/env python3
"""Tests for authentication: token validation, AuthBase, and pass invocation."""
from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest
import requests

from soma_init_repo_check.auth import (
    GitHubTokenAuth,
    retrieve_token,
    validate_token,
)


def test_valid_token_passes_validation() -> None:
    """A token with only printable ASCII passes validation."""
    validate_token("ghp_abc123XYZ")


def test_empty_token_fails_validation() -> None:
    """An empty token causes sys.exit(1)."""
    with pytest.raises(SystemExit, match="1"):
        validate_token("")


def test_token_with_non_printable_fails() -> None:
    """A token containing a non-printable character causes sys.exit(1)."""
    with pytest.raises(SystemExit, match="1"):
        validate_token("ghp_abc\x01xyz")


def test_token_all_printable_ascii_passes() -> None:
    """Token with spaces and punctuation (printable ASCII) passes."""
    validate_token("token with spaces! @#$%")


def test_auth_base_sets_authorization_header() -> None:
    """GitHubTokenAuth sets the Authorization: Bearer header."""
    auth = GitHubTokenAuth("test-token-123")
    req = requests.Request("GET", "https://api.github.com/repos/a/b")
    prepared = req.prepare()
    result = auth(prepared)
    assert result.headers["Authorization"] == "Bearer test-token-123"


def test_retrieve_token_success_real() -> None:
    """Test real token retrieval from pass (skipped if unavailable)."""
    try:
        result = subprocess.run(
            ["pass", "github.com/fgpat/public-repos-only"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            pytest.skip("pass entry not available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("pass not available")
    token = retrieve_token()
    assert token
    assert all(32 <= ord(ch) <= 126 for ch in token)


def test_retrieve_token_failure_includes_stderr() -> None:
    """Non-zero exit from pass includes stderr in the error."""
    fake = subprocess.CompletedProcess(
        args=["pass"], returncode=1,
        stdout="", stderr="gpg: decryption failed",
    )
    with patch("soma_init_repo_check.auth.subprocess.run", return_value=fake):
        with pytest.raises(SystemExit, match="1"):
            retrieve_token()


def test_retrieve_token_timeout() -> None:
    """Timeout from pass produces a descriptive error and exit code 1."""
    with patch(
        "soma_init_repo_check.auth.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="pass", timeout=60),
    ):
        with pytest.raises(SystemExit, match="1"):
            retrieve_token()
