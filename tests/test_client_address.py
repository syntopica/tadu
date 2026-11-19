import pytest

from tadu.client_address import client_address

PEER = "10.0.0.5"


@pytest.mark.parametrize(
    ("forwarded", "hops", "address"),
    [
        (None, 0, PEER),
        ("203.0.113.7", 0, PEER),
        ("203.0.113.7", 1, "203.0.113.7"),
        ("198.51.100.1, 203.0.113.7", 1, "203.0.113.7"),
        ("198.51.100.1, 203.0.113.7", 2, "198.51.100.1"),
        ("203.0.113.7", 2, PEER),
        ("", 1, PEER),
        ("not-an-address", 1, PEER),
        ("203.0.113.7, garbage", 1, PEER),
        ("  2001:db8::1 ", 1, "2001:db8::1"),
        ("2001:0db8:0000::0001", 1, "2001:db8::1"),
    ],
)
def test_read_as_werkzeug_proxyfix_reads_it(forwarded: str | None, hops: int, address: str) -> None:
    assert client_address(PEER, forwarded, hops) == address


def test_a_client_cannot_pick_its_address_past_the_trusted_proxies() -> None:
    # The client writes "1.2.3.4"; the one trusted proxy appends the address it saw.
    spoofed = "1.2.3.4, 203.0.113.7"
    assert client_address(PEER, spoofed, 1) == "203.0.113.7"
    assert client_address(PEER, spoofed, 0) == PEER
