from tadu.board_data_path import BOARD_DATA_PATH


def test_value() -> None:
    assert BOARD_DATA_PATH == "/api/cards"
