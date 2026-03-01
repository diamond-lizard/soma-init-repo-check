#!/usr/bin/env python3
"""Authentication: token retrieval from pass, validation, and AuthBase."""
from __future__ import annotations

import requests
from requests.auth import AuthBase
import subprocess
import sys


_PASS_ENTRY = "github.com/fgpat/public-repos-only"
_PASS_TIMEOUT = 60


def retrieve_token() -> str:
    """Retrieve the GitHub token from pass.

    Runs ``pass github.com/fgpat/public-repos-only`` with shell=False.
    Returns the first line of stdout as the token string.
    On failure, prints a descriptive error to stderr and exits with code 1.
    """
    try:
        result = subprocess.run(
            ["pass", _PASS_ENTRY],
            capture_output=True,
            text=True,
            shell=False,
            timeout=_PASS_TIMEOUT,
        )
    except FileNotFoundError:
        print("Error: 'pass' command not found on PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(
            f"Error: 'pass' timed out after {_PASS_TIMEOUT}s.",
            file=sys.stderr,
        )
        sys.exit(1)
    if result.returncode != 0:
        stderr_msg = result.stderr.strip()
        print(
            f"Error: 'pass' exited with code {result.returncode}: {stderr_msg}",
            file=sys.stderr,
        )
        sys.exit(1)
    first_line = result.stdout.split("\n", 1)[0].strip()
    if not first_line:
        print("Error: 'pass' returned an empty token.", file=sys.stderr)
        sys.exit(1)
    return first_line


def validate_token(token: str) -> None:
    """Validate that the token is non-empty printable ASCII (codes 32-126).

    If validation fails, prints a descriptive error to stderr suggesting
    the token may be misconfigured and exits with code 1.
    """
    if not token:
        print("Error: GitHub token is empty.", file=sys.stderr)
        sys.exit(1)
    for ch in token:
        if not (32 <= ord(ch) <= 126):
            print(
                "Error: GitHub token contains non-printable characters. "
                "The token may be misconfigured.",
                file=sys.stderr,
            )
            sys.exit(1)


class GitHubTokenAuth(AuthBase):
    """requests AuthBase subclass that injects Bearer token for GitHub API.

    Sets the Authorization header only on requests. The requests library
    automatically strips auth-based credentials on cross-host redirects,
    preventing token leakage to non-GitHub hosts.
    """

    def __init__(self, token: str) -> None:
        """Store the token for header injection."""
        self._token = token

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Attach the Authorization header to the request."""
        r.headers["Authorization"] = f"Bearer {self._token}"
        return r
