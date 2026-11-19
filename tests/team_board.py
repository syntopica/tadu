import itertools
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from board_server import BoardServer
from fake_github import FakeGithub, pkce_challenge
from response import Response

from tadu.allowed_hosts import allowed_hosts
from tadu.board_memory import board_memory
from tadu.board_state import BoardState
from tadu.cli import main
from tadu.make_board_handler import make_board_handler
from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS

NONCES = itertools.count()


@contextmanager
def serve_team_board(  # noqa: PLR0913 - one knob each for the sign-in, sessions and what the page may do
    workspace: Path,
    github: FakeGithub,
    public_url: str | None = None,
    *,
    idle_timeout: int = IDLE_TIMEOUT_SECONDS,
    allow: str = "read",
    **options: object,
) -> Iterator[BoardServer]:
    """A board signing in with the fake GitHub, its GitHub ids and sessions kept in the
    workspace as `tadu board` keeps them; behind `public_url`, requests name its host.
    `options` replace fields of the sign-in, such as `limiter` and `proxy_hops`; sessions
    end after `idle_timeout` seconds unused; the page may do what `allow` permits.
    """
    server = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    port = server.server_address[1]
    url = public_url or f"http://127.0.0.1:{port}"
    pins, sessions = board_memory(str(workspace), idle_timeout)
    sign_in = replace(github.sign_in(), public_url=url, pins=pins, sessions=sessions, **options)  # type: ignore[arg-type]
    hosts = allowed_hosts("127.0.0.1", port) | {urlsplit(url).netloc}
    state = BoardState(workspace, 14, "tok", hosts, allow, main, sign_in)
    server.RequestHandlerClass = make_board_handler(state)
    thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
    thread.start()
    try:
        host = urlsplit(url).netloc
        yield BoardServer(host, "tok", state, port)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def cookies(response: Response) -> dict[str, str]:
    """The name=value of each Set-Cookie."""
    pairs = (h.partition(";")[0].partition("=") for h in response.headers.get_all("Set-Cookie", []))
    return {name: value for name, _, value in pairs}


def call(board: BoardServer, method: str, path: str, cookie: str = "") -> Response:
    headers = {"Host": board.host} | ({"Cookie": cookie} if cookie else {})
    return board.request(method, path, headers)


def sign_in_as(board: BoardServer, login: str, prefix: str = "") -> str:
    """Walk the GitHub redirect as a browser would, with a fresh single-use code.

    Return the Cookie header to send; every sign-in gets its own GitHub token. `prefix`
    goes before the board's paths, as a proxy that keeps a subfolder sends them.
    """
    start = call(board, "GET", f"{prefix}/auth/login")
    (state_cookie, kept), *_ = cookies(start).items()
    state, _, verifier = kept.partition(".")
    query = parse_qs(urlsplit(start.headers["Location"]).query)
    assert query["state"] == [state]
    assert query["code_challenge"] == [pkce_challenge(verifier)]
    assert query["code_challenge_method"] == ["S256"]
    code = f"code-{login}~{next(NONCES)}"
    back = call(
        board,
        "GET",
        f"{prefix}/auth/callback?code={code}&state={state}",
        f"{state_cookie}={kept}",
    )
    assert back.status == 302, back.body
    (session_cookie, session), *_ = cookies(back).items()
    return f"{session_cookie}={session}"


def state_part(kept: str) -> str:
    """The state in a sign-in cookie's `state.verifier`, as the callback's link has it."""
    return kept.partition(".")[0]
