"""Host header values a board server accepts."""

from __future__ import annotations

from tadu.default_http_port import DEFAULT_HTTP_PORT


def allowed_hosts(host: str, port: int) -> frozenset[str]:
    """The bound address, plus `localhost` when bound to 127.0.0.1.

    Browsers omit the default port, so port 80 also allows the bare names.
    """
    names = {host, "localhost"} if host == "127.0.0.1" else {host}
    hosts = {f"{name}:{port}" for name in names}
    if port == DEFAULT_HTTP_PORT:
        hosts |= names
    return frozenset(hosts)
