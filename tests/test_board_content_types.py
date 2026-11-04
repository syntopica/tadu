from tadu.board_content_types import BOARD_CONTENT_TYPES


def test_every_type_declares_utf8() -> None:
    assert set(BOARD_CONTENT_TYPES) == {"index.html", "board.js", "board.css"}
    assert all(value.endswith("; charset=utf-8") for value in BOARD_CONTENT_TYPES.values())
