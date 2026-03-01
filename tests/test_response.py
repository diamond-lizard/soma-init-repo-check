#!/usr/bin/env python3
"""Tests for response processing pipeline."""
from __future__ import annotations

from io import BytesIO

import requests

from soma_init_repo_check.response import process_response


def _make_response(
    content: bytes = b'{"ok": true}',
    content_type: str = "application/json; charset=utf-8",
    content_length: str | None = None,
) -> requests.Response:
    """Build a requests.Response with controlled headers and body."""
    resp = requests.Response()
    resp.status_code = 200
    resp.headers["Content-Type"] = content_type
    if content_length is not None:
        resp.headers["Content-Length"] = content_length
    resp.raw = BytesIO(content)
    return resp


def test_valid_json_response_parsed() -> None:
    """A valid JSON response is parsed correctly."""
    resp = _make_response(b'{"fork": true}')
    data, err = process_response(resp)
    assert err is None
    assert data == {"fork": True}


def test_content_length_exceeding_10mb_rejected() -> None:
    """Response with Content-Length > 10 MB is rejected without reading."""
    resp = _make_response(content_length="20000000")
    data, err = process_response(resp)
    assert data is None
    assert "Content-Length" in err
    assert "10 MB" in err


def test_non_json_content_type_rejected() -> None:
    """Response with non-JSON Content-Type is rejected."""
    resp = _make_response(content_type="text/html")
    data, err = process_response(resp)
    assert data is None
    assert "Content-Type" in err


def test_streaming_body_exceeding_10mb_aborted() -> None:
    """Response body exceeding 10 MB during streaming is aborted."""
    large_body = b"x" * (10 * 1024 * 1024 + 1)
    resp = _make_response(content=large_body, content_type="application/json")
    resp.headers.pop("Content-Length", None)
    data, err = process_response(resp)
    assert data is None
    assert "10 MB" in err


def test_malformed_json_returns_error() -> None:
    """Malformed JSON response returns a descriptive error."""
    resp = _make_response(content=b"not json at all")
    data, err = process_response(resp)
    assert data is None
    assert "Invalid JSON" in err


def test_empty_json_object_parsed() -> None:
    """An empty JSON object is parsed successfully."""
    resp = _make_response(content=b"{}")
    data, err = process_response(resp)
    assert err is None
    assert data == {}


def test_content_length_at_limit_accepted() -> None:
    """Response with Content-Length exactly at 10 MB is accepted."""
    resp = _make_response(content_length=str(10 * 1024 * 1024))
    data, err = process_response(resp)
    assert err is None
