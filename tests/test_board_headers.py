from tadu.board_headers import BOARD_HEADERS


def test_values() -> None:
    assert BOARD_HEADERS == {
        "Content-Security-Policy": (
            "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; "
            "img-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'"
        ),
        "Referrer-Policy": "no-referrer",
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "no-store",
    }
    assert not any(name.lower().startswith("access-control") for name in BOARD_HEADERS)
