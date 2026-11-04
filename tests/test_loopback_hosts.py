from tadu.loopback_hosts import LOOPBACK_HOSTS


def test_values() -> None:
    assert frozenset({"127.0.0.1", "localhost"}) == LOOPBACK_HOSTS
