import pytest

from tadu.forge_remote_parts import forge_remote_parts


@pytest.mark.parametrize(
    "remote",
    [
        "git@github.com:acme/shop.git",
        "ssh://git@github.com/acme/shop",
        "https://github.com/acme/shop.git",
        "https://github.com/acme/shop/",
    ],
)
def test_forms(remote: str) -> None:
    assert forge_remote_parts(remote) == ("github.com", "acme/shop")


@pytest.mark.parametrize(
    "remote", ["http://github.com/acme/shop", "https://github.com/acme", "file:///x", ""]
)
def test_rejected(remote: str) -> None:
    assert forge_remote_parts(remote) is None
