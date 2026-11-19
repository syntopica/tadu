from http import HTTPStatus

import pytest

from tadu.github_sign_in import GithubSignIn
from tadu.request_cookies import request_cookies
from tadu.set_cookie import set_cookie
from tadu.text_response import text_response


def test_set_cookie_is_secure_behind_https() -> None:
    plain = GithubSignIn("id", "secret", "http://127.0.0.1:8123")
    tls = GithubSignIn("id", "secret", "https://board.example.com")
    assert set_cookie(plain, "a", "1", 60) == (
        "Set-Cookie",
        "a=1; Path=/; Max-Age=60; HttpOnly; SameSite=Lax",
    )
    assert set_cookie(tls, "a", "", 0) == (
        "Set-Cookie",
        "__Host-a=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax; Secure",
    )


def test_a_board_in_a_subfolder_keeps_its_cookies_to_it() -> None:
    tls = GithubSignIn("id", "secret", "https://example.com/tadu")
    plain = GithubSignIn("id", "secret", "http://10.0.0.5:8080/team/tadu")
    assert set_cookie(tls, "a", "1", 60) == (
        "Set-Cookie",
        "__Secure-a=1; Path=/tadu/; Max-Age=60; HttpOnly; SameSite=Lax; Secure",
    )
    assert set_cookie(plain, "a", "1", 60) == (
        "Set-Cookie",
        "a=1; Path=/team/tadu/; Max-Age=60; HttpOnly; SameSite=Lax",
    )


@pytest.mark.parametrize(
    ("url", "base", "host"),
    [
        ("https://tadu.mydomain.com", "", "tadu.mydomain.com"),
        ("https://mytadudomain.com", "", "mytadudomain.com"),
        ("https://mydomain.com/tadu", "/tadu", "mydomain.com"),
        ("http://127.0.0.1:8123/a/b", "/a/b", "127.0.0.1:8123"),
    ],
)
def test_where_the_board_is_served(url: str, base: str, host: str) -> None:
    sign_in = GithubSignIn("id", "secret", url)
    assert (sign_in.base_path, sign_in.public_host) == (base, host)


def test_the_secret_stays_out_of_repr() -> None:
    assert "secret" not in repr(GithubSignIn("id", "secret", "http://h:1"))


def test_request_cookies() -> None:
    assert request_cookies(None) == {}
    assert request_cookies("") == {}
    assert request_cookies("tadu_session=abc; theme=dark") == {
        "tadu_session": "abc",
        "theme": "dark",
    }
    assert request_cookies("tadu_session=x; tadu_session=y")["tadu_session"] == "x"


@pytest.mark.parametrize(
    "header",
    [
        "_ga=GA1.1.1234.5678; _gid=GA1.1.99; tadu_session=abc",
        'prefs={"theme":"dark","lang":"en"}; tadu_session=abc',
        "name=John Smith; tadu_session=abc",
        "list=a,b,c; tadu_session=abc",
        "city=Zürich; tadu_session=abc".encode().decode("latin-1"),
        "cart=[1,2]; tadu_session=abc",
        "odd; a=1;,b=2; =3; tadu_session=abc",
    ],
)
def test_other_cookies_on_the_host_never_hide_the_session(header: str) -> None:
    # http.cookies.SimpleCookie loses the session after the JSON, the space and the accent.
    assert request_cookies(header)["tadu_session"] == "abc"


def test_text_response_points_back() -> None:
    status, body, content_type = text_response(HTTPStatus.BAD_REQUEST, "Sign-in failed: x.")
    assert status == 400
    assert body == b"Sign-in failed: x.\n\nOpen the board's address again to sign in.\n"
    assert content_type == "text/plain; charset=utf-8"
