import argparse

import pytest

from tadu.public_board_url import public_board_url


@pytest.mark.parametrize(
    ("text", "url"),
    [
        ("https://board.example.com", "https://board.example.com"),
        ("https://Board.Example.com/", "https://board.example.com"),
        ("https://board.example.com:443", "https://board.example.com"),
        ("https://board.example.com:8443/", "https://board.example.com:8443"),
        ("http://127.0.0.1:8123", "http://127.0.0.1:8123"),
        ("http://localhost:80", "http://localhost"),
        (" https://b.example ", "https://b.example"),
    ],
)
def test_accepted_as_a_host_header_has_it(text: str, url: str) -> None:
    assert public_board_url(text) == url


@pytest.mark.parametrize(
    ("text", "url"),
    [
        ("https://example.com/tadu", "https://example.com/tadu"),
        ("https://Example.com/tadu/", "https://example.com/tadu"),
        ("https://example.com:443/Team-Board", "https://example.com/Team-Board"),
        ("https://example.com/tools/tadu", "https://example.com/tools/tadu"),
        ("https://example.com/tools/api", "https://example.com/tools/api"),
        ("http://10.0.0.5:8080/v1.2_x~y/", "http://10.0.0.5:8080/v1.2_x~y"),
        ("https://example.com/apis", "https://example.com/apis"),
    ],
)
def test_a_subfolder_keeps_its_path_without_the_trailing_slash(text: str, url: str) -> None:
    assert public_board_url(text) == url


@pytest.mark.parametrize(
    "text",
    [
        "board.example.com",
        "ftp://board.example.com",
        "https://",
        "https://board.example.com/?x=1",
        "https://board.example.com/#top",
        "https://user@board.example.com",
        "https://board.example.com:99999",
        "https://board.example.com:port",
        "https://example.com/tadu?x=1",
        "https://example.com/tadu#top",
        "https://example.com//tadu",
        "https://example.com/tadu//board",
        "https://example.com/../tadu",
        "https://example.com/tadu/..",
        "https://example.com/./tadu",
        "https://example.com/ta%20du",
        "https://example.com/ta du",
        "https://example.com/tädu",
        "https://example.com/api",
        "https://example.com/auth/",
        "https://example.com/api/tadu",
        "https://example.com/app.js",
        "https://example.com/board.css/tadu",
        "https://example.com/index.html",
    ],
)
def test_rejected(text: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match="must be http:// or https://"):
        public_board_url(text)
