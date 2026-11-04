from tadu.board_cookie import board_cookie


def test_value() -> None:
    assert board_cookie("t") == "tadu_board=t; HttpOnly; SameSite=Strict; Path=/"
