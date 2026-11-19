"""Check from the outside that a running board uses the settings it was given."""

import json
import socket
import time
from urllib.parse import parse_qs, urlsplit

from board_run import RunningBoard, Settings, check_cards
from board_server import Response
from team_board import cookies, state_part

SIGNING_IN = "192.0.2.1"  # the address a person signs in from, behind the proxy


def check_board(board: RunningBoard, expected: Settings) -> None:
    """Every setting: address, workspace, done window, then how people get in."""
    port = board.server.server_address[1]
    if expected.port is not None:
        assert port == expected.port
    check_address(board, expected.host)
    assert board.state.workspace == expected.workspace
    assert board.state.done_days == expected.done_days
    if expected.auth == "token":
        check_token_board(board, expected)
    else:
        check_team_board(board, expected)


def check_address(board: RunningBoard, host: str) -> None:
    """Bound to the host's address, and answering its Host header only, with the port."""
    address, port = board.server.server_address[:2]
    assert address == socket.gethostbyname(host)
    assert get(board, "/app.js", {"Host": f"{host}:{port}"}).status == 200
    for other in ("127.0.0.1", "localhost", "127.0.0.2"):
        if other != host and not (host == "127.0.0.1" and other == "localhost"):
            assert get(board, "/app.js", {"Host": f"{other}:{port}"}).status == 421, other


def check_token_board(board: RunningBoard, expected: Settings) -> None:
    """The single-person board: the printed URL opens it and its cards."""
    host = f"{expected.host}:{board.server.server_address[1]}"
    assert board.output.getvalue() == f"http://{host}/?token={board.state.token}\n"
    assert board.state.github is None
    answer = board.request("GET", f"/api/cards?token={board.state.token}", {"Host": host})
    assert answer.status == 200
    check_cards(json.loads(answer.body), expected)


def check_team_board(board: RunningBoard, expected: Settings) -> None:
    """Signing in with GitHub at the public URL, then the limits on signing in."""
    public = expected.public_url or f"http://{expected.host}:{board.server.server_address[1]}"
    assert board.output.getvalue() == f"{public}/\n"
    parts = urlsplit(public)
    assert get(board, f"{parts.path}/", browser("evil.example")).status == 421
    cookie = sign_in(board, public)
    cards = get(board, f"{parts.path}/api/cards", browser(parts.netloc, cookie=cookie))
    assert cards.status == 200
    check_cards(json.loads(cards.body), expected)
    session = get(board, f"{parts.path}/api/session", browser(parts.netloc, cookie=cookie))
    remaining = json.loads(session.body)["remaining"]
    assert expected.idle_timeout - 5 <= remaining <= expected.idle_timeout
    check_limits(board, expected, parts.netloc, f"{parts.path}/auth/login")


def browser(host: str, *, forwarded: str = SIGNING_IN, cookie: str = "") -> dict[str, str]:
    """The headers a browser sends through the proxy."""
    return {"Host": host, "X-Forwarded-For": forwarded} | ({"Cookie": cookie} if cookie else {})


def get(board: RunningBoard, path: str, headers: dict[str, str]) -> Response:
    return board.request("GET", path, headers)


def sign_in(board: RunningBoard, public: str) -> str:
    """Ana-Dev through the fake GitHub, as a browser; the session's Cookie header."""
    parts = urlsplit(public)
    start = get(board, f"{parts.path}/auth/login", browser(parts.netloc))
    assert start.status == 302
    query = parse_qs(urlsplit(start.headers["Location"]).query)
    assert query["redirect_uri"] == [f"{public}/auth/callback"]
    ((name, state),) = cookies(start).items()
    code = f"code-Ana-Dev~{time.monotonic_ns()}"
    callback = f"{parts.path}/auth/callback?code={code}&state={state_part(state)}"
    back = get(board, callback, browser(parts.netloc, cookie=f"{name}={state}"))
    assert back.status == 302, back.body
    assert back.headers["Location"] == f"{parts.path}/"
    session = next(pair for pair in cookies(back).items() if pair[1])
    return "=".join(session)


def check_limits(board: RunningBoard, expected: Settings, host: str, path: str) -> None:
    """The limit per address; behind trusted proxies, each forwarded address has its own.

    Without them the forwarded address is ignored, so every request counts as the
    connection's, which already signed in once.
    """
    limit = expected.sign_in_limit
    if expected.proxy_hops:
        answers = [
            get(board, path, browser(host, forwarded="198.51.100.7")).status
            for _ in range(limit + 1)
        ]
        assert answers == [302] * limit + [429]
        assert get(board, path, browser(host, forwarded="198.51.100.8")).status == 302
    else:
        answers = [
            get(board, path, browser(host, forwarded=f"198.51.100.{n}")).status
            for n in range(limit)
        ]
        assert answers == [302] * (limit - 1) + [429]
