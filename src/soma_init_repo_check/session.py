#!/usr/bin/env python3
"""GitHub API session setup with requests-cache SQLite backend."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import requests_cache
    from requests.auth import AuthBase


_APP_NAME = "soma-init-repo-check"
_CACHE_SUBDIR = "etags"
_HASH_LENGTH = 16


def compute_cache_path(emacs_dir: str) -> Path:
    """Compute the SQLite cache database path for the given emacs-dir.

    Path format: $XDG_CACHE_HOME/<app>/etags/<hash>.sqlite
    Falls back to ~/.cache/<app>/etags/<hash>.sqlite when XDG is unset.
    The <hash> is the first 16 hex chars of SHA-256 of the resolved path.

    Input: emacs_dir — the --emacs-dir CLI argument string.
    Output: pathlib.Path to the SQLite cache database file.
    """
    resolved = str(Path(emacs_dir).expanduser().resolve())
    digest = hashlib.sha256(resolved.encode("utf-8")).hexdigest()
    short_hash = digest[:_HASH_LENGTH]
    xdg = os.environ.get("XDG_CACHE_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / _APP_NAME / _CACHE_SUBDIR / f"{short_hash}.sqlite"

_DIR_MODE = 0o700
_FILE_MODE = 0o600


def ensure_cache_dir(cache_path: Path) -> None:
    """Create the cache directory with mode 0700 if it does not exist.

    After the CachedSession creates the SQLite file, call
    secure_cache_file() to set its permissions to 0600.

    Input: cache_path — Path to the SQLite database file.
    Output: None. Creates directories as a side effect.
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True, mode=_DIR_MODE)


def secure_cache_file(cache_path: Path) -> None:
    """Set the SQLite database file permissions to mode 0600.

    Input: cache_path — Path to the SQLite database file.
    Output: None. Changes file permissions as a side effect.
    """
    if cache_path.exists():
        cache_path.chmod(_FILE_MODE)


def create_session(cache_path: Path, auth: AuthBase) -> requests_cache.CachedSession:
    """Create a requests_cache.CachedSession with SQLite backend.

    Configures: SQLite backend at cache_path, expire_after=0 for forced
    revalidation (ETag-based conditional requests), auth instance, and
    required GitHub API headers.

    Input: cache_path — Path to the SQLite database file.
           auth — AuthBase subclass instance for token injection.
    Output: A configured CachedSession ready for API calls.
    """
    import requests_cache

    ensure_cache_dir(cache_path)
    session = requests_cache.CachedSession(
        str(cache_path.with_suffix("")),
        backend="sqlite",
        expire_after=0,
    )
    session.auth = auth
    session.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "soma-init-repo-check",
    })
    secure_cache_file(cache_path)
    return session
