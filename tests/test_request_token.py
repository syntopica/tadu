from tadu.request_token import request_token


def test_query_parameter_wins_over_header() -> None:
    assert request_token("/api/cards?a=1&token=q", "h") == "q"


def test_header_when_no_query_parameter() -> None:
    assert request_token("/api/cards", "h") == "h"


def test_none_without_either() -> None:
    assert request_token("/api/cards?x=1", None) is None
