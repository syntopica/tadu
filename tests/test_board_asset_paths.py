from tadu.board_asset_paths import BOARD_ASSET_PATHS


def test_index_is_served_at_root_only() -> None:
    assert BOARD_ASSET_PATHS == {
        "/": "index.html",
        "/filters.js": "filters.js",
        "/board.js": "board.js",
        "/board.css": "board.css",
    }
