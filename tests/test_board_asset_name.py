from tadu.board_asset_name import board_asset_name


def test_index_only_at_root() -> None:
    assert board_asset_name("/") == "index.html"
    assert board_asset_name("/index.html") == ""


def test_other_paths_drop_the_slash() -> None:
    assert board_asset_name("/app.js") == "app.js"
    assert board_asset_name("/a/b.js") == "a/b.js"
    assert board_asset_name("app.js") == ""
