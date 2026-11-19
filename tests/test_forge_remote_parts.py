import pytest

from tadu.forge_remote_parts import forge_remote_parts


@pytest.mark.parametrize(
    "remote",
    [
        "git@github.com:acme/shop.git",
        "github.com:acme/shop.git",
        "ssh://git@github.com/acme/shop",
        "ssh://git@github.com:22/acme/shop.git",
        "git+ssh://git@github.com/acme/shop.git",
        "git://github.com/acme/shop.git",
        "https://github.com/acme/shop.git",
        "https://user@GitHub.com/acme/shop.git",
        "https://github.com/acme/shop/",
        " https://github.com/acme/shop.git ",
    ],
)
def test_forms(remote: str) -> None:
    assert forge_remote_parts(remote) == ("github.com", "acme/shop")


def test_subgroups_keep_their_whole_path() -> None:
    assert forge_remote_parts("https://gitlab.com/group/sub/shop.git") == (
        "gitlab.com",
        "group/sub/shop",
    )
    assert forge_remote_parts("git@gitlab.com:group/sub/shop.git") == (
        "gitlab.com",
        "group/sub/shop",
    )


@pytest.mark.parametrize(
    "remote",
    [
        "http://github.com/acme/shop",
        "https://github.com/acme",
        "https://github.com//shop",
        "file:///x",
        "/srv/git/shop",
        "C:\\repos\\shop",
        "shop",
        "",
    ],
)
def test_rejected(remote: str) -> None:
    assert forge_remote_parts(remote) is None
