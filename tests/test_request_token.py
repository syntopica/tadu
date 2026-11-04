from tadu.request_token import request_token


def test_query_parameter_wins_over_cookie() -> None:
    assert request_token("/?a=1&token=q", "tadu_board=c") == "q"


def test_cookie_when_no_query_parameter() -> None:
    assert request_token("/api/cards", "other=1; tadu_board=c") == "c"


def test_none_without_either() -> None:
    assert request_token("/?x=1", None) is None
    assert request_token("/", "other=1") is None


def test_malformed_neighbours_do_not_hide_the_cookie() -> None:
    assert request_token("/", 'a=1; expires; "x; tadu_board=c; tadu_board=d') == "c"
    assert request_token("/", "tadu_board; =;;") is None
