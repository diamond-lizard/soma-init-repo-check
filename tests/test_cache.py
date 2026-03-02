#!/usr/bin/env python3
"""Tests for stale cache entry cleanup using a real CachedSession."""
from __future__ import annotations

from pathlib import Path

import requests
import requests_cache
import urllib3

from soma_init_repo_check.cache import cleanup_stale_entries


def _make_cached_session(tmp_path: Path) -> requests_cache.CachedSession:
    """Create a CachedSession with a temp SQLite backend."""
    db = tmp_path / "test_cache"
    return requests_cache.CachedSession(str(db), backend="sqlite")


def _seed_url(session: requests_cache.CachedSession, url: str) -> None:
    """Seed a synthetic cached response for the given URL."""
    resp = requests.Response()
    resp.status_code = 200
    resp._content = b'{"ok": true}'
    resp.headers["Content-Type"] = "application/json"
    req = requests.Request("GET", url).prepare()
    resp.request = req
    resp.url = url
    resp.raw = urllib3.HTTPResponse(
        body=b'{"ok": true}', status=200, request_url=url,
    )
    session.cache.save_response(resp)


def test_stale_entries_are_removed(tmp_path: Path) -> None:
    """Cached URLs not in the requested set are deleted."""
    session = _make_cached_session(tmp_path)
    _seed_url(session, "https://api.github.com/repos/a/b")
    _seed_url(session, "https://api.github.com/repos/c/d")
    _seed_url(session, "https://api.github.com/repos/e/f")
    requested = frozenset({"https://api.github.com/repos/a/b"})
    cleanup_stale_entries(session, requested)
    remaining = set(session.cache.urls())
    assert "https://api.github.com/repos/a/b" in remaining
    assert "https://api.github.com/repos/c/d" not in remaining
    assert "https://api.github.com/repos/e/f" not in remaining


def test_non_stale_entries_are_preserved(tmp_path: Path) -> None:
    """Cached URLs in the requested set are kept."""
    session = _make_cached_session(tmp_path)
    url1 = "https://api.github.com/repos/a/b"
    url2 = "https://api.github.com/repos/c/d"
    _seed_url(session, url1)
    _seed_url(session, url2)
    requested = frozenset({url1, url2})
    cleanup_stale_entries(session, requested)
    remaining = set(session.cache.urls())
    assert url1 in remaining
    assert url2 in remaining


def test_empty_requested_set_removes_all(tmp_path: Path) -> None:
    """An empty requested set removes all cached entries."""
    session = _make_cached_session(tmp_path)
    _seed_url(session, "https://api.github.com/repos/a/b")
    _seed_url(session, "https://api.github.com/repos/c/d")
    cleanup_stale_entries(session, frozenset())
    assert session.cache.urls() == []


def test_no_cached_entries_is_noop(tmp_path: Path) -> None:
    """Cleanup with no cached entries does nothing."""
    session = _make_cached_session(tmp_path)
    cleanup_stale_entries(session, frozenset({"https://example.com"}))
    assert session.cache.urls() == []
