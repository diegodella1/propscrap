"""Validate outbound / configured URLs (HTTPS, no obvious SSRF targets)."""

from __future__ import annotations

import ipaddress
from urllib.parse import urlparse


def assert_public_https_url(url: str, *, label: str = "URL") -> None:
    """Require https and block localhost / link-local / private IPs in the hostname."""
    parsed = urlparse(url.strip())
    if parsed.scheme != "https":
        msg = f"{label} must use https"
        raise ValueError(msg)
    host = (parsed.hostname or "").lower()
    if not host:
        msg = f"{label} must include a valid hostname"
        raise ValueError(msg)
    if host in {"localhost", "127.0.0.1", "::1", "0.0.0.0"}:
        msg = f"{label} cannot target loopback or wildcard addresses"
        raise ValueError(msg)
    if host.endswith(".local") or host.endswith(".localhost"):
        msg = f"{label} cannot target local-only hostnames"
        raise ValueError(msg)
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        msg = f"{label} cannot target private or non-public addresses"
        raise ValueError(msg)
