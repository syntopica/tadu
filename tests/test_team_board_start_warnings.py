"""What a board signing in with GitHub warns about when it starts, beyond the basics."""

import time
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from board_run import second_loopback
from team_workspace import team_workspace

from tadu.cli import main
from tadu.session_store import SessionStore
from tadu.token_grant import TokenGrant


def test_a_shortened_idle_timeout_ends_longer_saved_sessions(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    workspace = team_workspace(tmp_path)
    saved = SessionStore(workspace / "tadu-workspace.sessions.json")
    cookie = saved.create("Ana-Dev", TokenGrant("tok", None, None), time.time())
    argv = ["board", "--workspace", str(workspace), "--port", "0", "--auth", "github"]
    assert main([*argv, "--idle-timeout", "30m"]) == 0
    assert (
        "tadu board: warning: 1 saved session(s) had longer to last than --idle-timeout "
        "and ended; they sign in again\n"
    ) in capsys.readouterr().err
    state = serving[0].RequestHandlerClass.state  # type: ignore[attr-defined]
    assert state.github.sessions.idle_timeout == 1800
    assert state.github.sessions.find(cookie, time.time()) is None


def test_trusting_proxies_while_reachable_without_them_is_warned_about(
    tmp_path: Path, serving: list[ThreadingHTTPServer], capsys: pytest.CaptureFixture[str]
) -> None:
    host = second_loopback()
    argv = ["board", "--workspace", str(team_workspace(tmp_path)), "--port", "0"]
    url = ["--public-url", "https://board.example.com", "--proxy-hops", "1"]
    assert main([*argv, "--auth", "github", "--host", host, *url]) == 0
    assert (
        f"tadu board: warning: --proxy-hops trusts X-Forwarded-For, but the board listens on "
        f"{host}, so a client that reaches it without the proxy chooses the address its "
        "sign-in limit counts: listen on 127.0.0.1 behind the proxy\n"
    ) in capsys.readouterr().err
    assert serving
