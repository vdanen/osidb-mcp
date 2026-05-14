"""Lazy OSIDB session (JWT refresh handled by osidb-bindings)."""

from __future__ import annotations

import osidb_bindings
from osidb_bindings.session import Session

from osidb_mcp.config import Settings

_session: Session | None = None
_settings: Settings | None = None


def configure(settings: Settings) -> None:
    """Store settings and drop any existing session (e.g. after reconfigure)."""
    global _settings, _session
    _settings = settings
    _session = None


def _ensure_session() -> Session:
    global _session
    if _session is not None:
        return _session
    if _settings is None:
        raise RuntimeError("osidb-mcp not configured (missing settings)")
    s = _settings
    if s.auth == "basic":
        _session = osidb_bindings.new_session(
            osidb_server_uri=s.base_url,
            username=s.username,
            password=s.password,
            verify_ssl=s.verify_ssl,
            user_agent=s.user_agent,
        )
    else:
        _session = osidb_bindings.new_session(
            osidb_server_uri=s.base_url,
            verify_ssl=s.verify_ssl,
            user_agent=s.user_agent,
        )
    return _session


def get_session() -> Session:
    return _ensure_session()


def current_settings() -> Settings:
    if _settings is None:
        raise RuntimeError("osidb-mcp not configured")
    return _settings
