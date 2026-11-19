import pytest

from tadu.github_repository import github_repository
from tadu.repository_entry import RepositoryEntry


@pytest.mark.parametrize(
    ("remote", "expected"),
    [
        ("https://github.com/acme/shop", "acme/shop"),
        ("https://github.com/Acme/Shop.git", "acme/shop"),
        ("git@GitHub.com:acme/shop.git", "acme/shop"),
        ("ssh://git@github.com/acme/shop", "acme/shop"),
        ("https://gitlab.com/acme/shop", None),
        ("https://github.example.com/acme/shop", None),
        ("https://github.com/acme/shop/tree/main", None),
        ("ssh://git@github.com:22/Acme/Shop.git", "acme/shop"),
        ("/srv/git/shop", None),
        ("https://github.com/acme/..", None),
        ("https://github.com/acme/.", None),
        ("https://github.com/../user", None),
        ("https://github.com/acme/shop%2F..", None),
        ("https://github.com/-acme/shop", None),
        ("https://github.com/ac--me/shop", "ac--me/shop"),  # older accounts have these
        ("https://github.com/acme/sh op", None),
        ("https://github.com/acme/shop?tab=readme", "acme/shop"),
        ("https://github.com/my-org/my.repo_v2", "my-org/my.repo_v2"),
        ("https://github.com/acme/.github", "acme/.github"),
        (None, None),
    ],
)
def test_only_github_com_remotes(remote: str | None, expected: str | None) -> None:
    assert github_repository(RepositoryEntry("shop", remote)) == expected
