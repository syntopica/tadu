from response import Response

from tadu.board_headers import BOARD_HEADERS


def check_board_headers(response: Response) -> None:
    """The response carries the board's security headers and no CORS header."""
    for name, value in BOARD_HEADERS.items():
        assert response.headers[name] == value
    assert not any(h.lower().startswith("access-control") for h in response.headers)
