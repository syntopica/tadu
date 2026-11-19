"""The address of the person behind a request."""

from __future__ import annotations

import ipaddress


def client_address(peer: str, forwarded_for: str | None, proxy_hops: int) -> str:
    """The peer's address, or the one `proxy_hops` trusted proxies say they forwarded.

    The same reading as Werkzeug's ProxyFix: each proxy appends the address it got the
    request from to X-Forwarded-For, so with N proxies in front the client is the N-th
    entry from the right. The header is not read at all with no trusted proxy, since
    anyone can send it; a header with too few entries, or an entry that is no address,
    leaves the peer's.
    """
    if proxy_hops < 1 or not forwarded_for:
        return peer
    entries = [entry.strip() for entry in forwarded_for.split(",")]
    if len(entries) < proxy_hops:
        return peer
    try:
        return str(ipaddress.ip_address(entries[-proxy_hops]))
    except ValueError:
        return peer
