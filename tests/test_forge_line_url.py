from tadu.forge_line_url import forge_line_url


def test_github_both_forms() -> None:
    want = "https://github.com/acme/shop/blob/HEAD/TODO.md#L3"
    assert forge_line_url("git@github.com:acme/shop.git", "TODO.md", 3) == want
    assert forge_line_url("https://github.com/acme/shop", "TODO.md", 3) == want


def test_gitlab() -> None:
    got = forge_line_url("git@gitlab.com:acme/shop.git", "a b/TODO.md", 7)
    assert got == "https://gitlab.com/acme/shop/-/blob/HEAD/a%20b/TODO.md#L7"


def test_unknown_host_and_none() -> None:
    assert forge_line_url("git@example.org:acme/shop.git", "TODO.md", 1) is None
    assert forge_line_url(None, "TODO.md", 1) is None
