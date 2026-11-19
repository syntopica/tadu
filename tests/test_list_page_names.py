import pytest

from tadu.github_reply import GithubReply
from tadu.last_page import last_page
from tadu.list_page_names import list_page_names

LINKS = {
    "next": {"url": "https://api.github.com/user/repos?per_page=100&page=2", "rel": "next"},
    "last": {"url": "https://api.github.com/user/repos?per_page=100&page=7", "rel": "last"},
}


def test_readable_names_in_lowercase_with_ids_and_the_page_count() -> None:
    body = [
        {"id": 1, "full_name": "Acme/Shop", "permissions": {"pull": True}},
        {"id": 2, "full_name": "acme/vault", "permissions": {"pull": False}},
        {"id": 3, "full_name": "acme/plain"},
        {"id": 4, "full_name": 3},
        {"id": "5", "full_name": "acme/text-id"},
        {"id": True, "full_name": "acme/bool-id"},
        {"full_name": "acme/no-id"},
        {"name": "nameless"},
        "not an object",
    ]
    assert list_page_names(GithubReply(200, body, None, LINKS)) == (
        (("acme/shop", 1), ("acme/plain", 3)),
        7,
    )


def test_a_body_that_is_no_list_holds_nothing() -> None:
    assert list_page_names(GithubReply(200, {"message": "?"})) == ((), 1)


@pytest.mark.parametrize(
    ("links", "pages"),
    [
        ({}, 1),
        (LINKS, 7),
        ({"last": {"url": "https://api.github.com/user/repos?page=12&per_page=100"}}, 12),
        ({"prev": {"url": "https://api.github.com/user/repos?page=1"}}, 1),
        ({"last": {"url": "https://api.github.com/user/repos?page=x"}}, 1),
        ({"last": {}}, 1),
    ],
)
def test_last_page(links: dict[str, dict[str, str]], pages: int) -> None:
    assert last_page(links) == pages
