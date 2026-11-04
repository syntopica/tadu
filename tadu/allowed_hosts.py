"""Host header values a board server accepts."""

from __future__ import annotations


def allowed_hosts(host: str, port: int) -> frozenset[str]:
    """The bound address, plus `localhost` when bound to 127.0.0.1."""
    hosts = {f"{host}:{port}"}
    if host == "127.0.0.1":
        hosts.add(f"localhost:{port}")
    return frozenset(hosts)
