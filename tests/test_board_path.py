import pytest

from tadu.board_path import board_path


@pytest.mark.parametrize(
    ("path", "base", "mapped"),
    [
        ("/", "", "/"),
        ("/api/cards", "", "/api/cards"),
        ("/tadu/api/cards", "", "/tadu/api/cards"),
        ("/tadu/", "/tadu", "/"),
        ("/tadu/api/cards", "/tadu", "/api/cards"),
        ("/tadu/auth/callback?code=c&state=s", "/tadu", "/auth/callback?code=c&state=s"),
        ("/api/cards", "/tadu", "/api/cards"),
        ("/", "/tadu", "/"),
        ("/?token=t", "/tadu", "/?token=t"),
        ("/tools/tadu/app.js", "/tools/tadu", "/app.js"),
        ("/taduX/app.js", "/tadu", "/taduX/app.js"),
        ("/x/tadu/app.js", "/tadu", "/x/tadu/app.js"),
        ("/tadu/tadu/app.js", "/tadu", "/tadu/app.js"),
    ],
)
def test_with_or_without_the_subfolder(path: str, base: str, mapped: str) -> None:
    assert board_path(path, base) == mapped


@pytest.mark.parametrize("path", ["/tadu", "/tadu?x=1", "/tadu?"])
def test_the_bare_subfolder_is_none(path: str) -> None:
    assert board_path(path, "/tadu") is None
