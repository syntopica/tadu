import pytest

from tadu.board_asset import board_asset


@pytest.mark.parametrize(
    ("name", "content_type"),
    [
        ("index.html", "text/html; charset=utf-8"),
        ("board.js", "text/javascript; charset=utf-8"),
        ("filters.js", "text/javascript; charset=utf-8"),
        ("board.css", "text/css; charset=utf-8"),
    ],
)
def test_known_assets(name: str, content_type: str) -> None:
    asset = board_asset(name)
    assert asset is not None
    assert asset[1] == content_type
    assert asset[0]


@pytest.mark.parametrize(
    "name", ["", "../cli.py", "rule_block_v3.md", "board/index.html", "missing.js", "a/b.js"]
)
def test_unknown_names(name: str) -> None:
    assert board_asset(name) is None
