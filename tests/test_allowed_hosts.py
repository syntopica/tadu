from tadu.allowed_hosts import allowed_hosts


def test_loopback_also_allows_localhost() -> None:
    assert allowed_hosts("127.0.0.1", 8080) == frozenset({"127.0.0.1:8080", "localhost:8080"})


def test_other_host_allows_only_itself() -> None:
    assert allowed_hosts("192.168.1.5", 8080) == frozenset({"192.168.1.5:8080"})


def test_port_80_also_allows_the_bare_host() -> None:
    assert allowed_hosts("192.168.1.5", 80) == frozenset({"192.168.1.5:80", "192.168.1.5"})
    assert allowed_hosts("127.0.0.1", 80) == frozenset(
        {"127.0.0.1:80", "localhost:80", "127.0.0.1", "localhost"}
    )


def test_other_ports_still_require_the_port() -> None:
    assert "127.0.0.1" not in allowed_hosts("127.0.0.1", 8080)
    assert "localhost" not in allowed_hosts("127.0.0.1", 8080)
