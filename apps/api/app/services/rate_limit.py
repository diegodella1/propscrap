"""Simple in-memory sliding-window rate limiting for sensitive routes."""

from __future__ import annotations

from collections import deque
from time import monotonic

from fastapi import Request
from app.errors import RateLimitError

_AUTH_WINDOW_SECONDS = 60.0
_AUTH_MAX_REQUESTS = 30
_auth_buckets: dict[str, deque[float]] = {}


def _client_key(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def enforce_auth_rate_limit(request: Request) -> None:
    """Limit login/signup bursts per client IP."""
    now = monotonic()
    key = _client_key(request)
    bucket = _auth_buckets.setdefault(key, deque())
    while bucket and now - bucket[0] > _AUTH_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= _AUTH_MAX_REQUESTS:
        raise RateLimitError("Too many authentication attempts. Try again later.")
    bucket.append(now)
