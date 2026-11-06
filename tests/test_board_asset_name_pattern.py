import pytest

from tadu.board_asset_name_pattern import BOARD_ASSET_NAME_PATTERN


@pytest.mark.parametrize("name", ["app.js", "board.css", "index.html", "card-visible.js", "a1.js"])
def test_accepts(name: str) -> None:
    assert BOARD_ASSET_NAME_PATTERN.fullmatch(name)


@pytest.mark.parametrize(
    "name",
    ["", "-a.js", "App.js", "a_b.js", "a.py", "a/b.js", "../a.js", ".js", "a.js\n", "a.json"],
)
def test_refuses(name: str) -> None:
    assert BOARD_ASSET_NAME_PATTERN.fullmatch(name) is None
