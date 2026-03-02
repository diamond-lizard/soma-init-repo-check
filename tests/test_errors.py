#!/usr/bin/env python3
"""Tests for HTTP error classification, threshold, and orchestration."""
from __future__ import annotations


from soma_init_repo_check.errors import classify_http_error
from soma_init_repo_check.errors import classify_network_error
from soma_init_repo_check.errors import extract_host
from soma_init_repo_check.errors import is_server_error
from soma_init_repo_check.error_tracker import HostErrorTracker


def test_404_produces_auth_note() -> None:
    """A 404 error message mentions possible deleted repo or permissions."""
    msg = classify_http_error(404, "owner/repo")
    assert "404" in msg
    assert "deleted" in msg or "permissions" in msg


def test_other_4xx_produces_error() -> None:
    """A 422 error produces a generic error message."""
    msg = classify_http_error(422, "owner/repo")
    assert "422" in msg
    assert "owner/repo" in msg


def test_5xx_is_server_error() -> None:
    """500, 502, 503 are server errors."""
    assert is_server_error(500) is True
    assert is_server_error(502) is True
    assert is_server_error(503) is True


def test_4xx_is_not_server_error() -> None:
    """4xx codes are not server errors."""
    assert is_server_error(404) is False
    assert is_server_error(422) is False


def test_network_error_message() -> None:
    """Network error produces descriptive message with exception type."""
    exc = ConnectionError("Connection refused")
    msg = classify_network_error(exc, "owner/repo")
    assert "ConnectionError" in msg
    assert "owner/repo" in msg


def test_extract_host_from_url() -> None:
    """Extract hostname from a GitHub API URL."""
    host = extract_host("https://api.github.com/repos/a/b")
    assert host == "api.github.com"


def test_tracker_counts_errors() -> None:
    """HostErrorTracker increments counts per host."""
    tracker = HostErrorTracker()
    tracker.add_errors("api.github.com", 1)
    assert tracker.get_count("api.github.com") == 1
    tracker.add_errors("api.github.com", 2)
    assert tracker.get_count("api.github.com") == 3


def test_tracker_threshold_at_five() -> None:
    """Threshold triggers at 5 errors from a single host."""
    tracker = HostErrorTracker()
    tracker.add_errors("api.github.com", 4)
    assert tracker.check_threshold("api.github.com") is False
    tracker.add_errors("api.github.com", 1)
    assert tracker.check_threshold("api.github.com") is True


def test_5xx_successful_retry_zero_errors() -> None:
    """A 5xx with successful retry counts as 0 errors."""
    tracker = HostErrorTracker()
    tracker.add_errors("api.github.com", 0)
    assert tracker.get_count("api.github.com") == 0


def test_5xx_failed_retry_two_errors() -> None:
    """A 5xx with failed retry counts as 2 errors."""
    tracker = HostErrorTracker()
    tracker.add_errors("api.github.com", 2)
    assert tracker.get_count("api.github.com") == 2


def test_threshold_abort_at_five() -> None:
    """Per-host error count triggers abort at exactly 5 errors."""
    tracker = HostErrorTracker()
    for _ in range(4):
        tracker.add_errors("api.github.com", 1)
        assert tracker.check_threshold("api.github.com") is False
    tracker.add_errors("api.github.com", 1)
    assert tracker.check_threshold("api.github.com") is True
