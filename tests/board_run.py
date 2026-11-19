"""Run `tadu board` for real, as its command line and config files set it, and check
from the outside that it uses what they say: the bound address, the workspace, the
done window, the sign-in, the public URL, the sign-in limit and the trusted proxies.
"""

import functools
import io
import socket
import sys
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from fake_github import SECRET, FakeGithub
from response import Response
from send_request import send_request
from team_workspace import team_workspace

from tadu.board_state import BoardState
from tadu.cli import main
from tadu.github_sign_in import GithubSignIn

CLOSED = "Shipped five days ago"


@dataclass(frozen=True)
class Settings:
    """What the board should turn out to use; `port` None is any port."""

    workspace: Path
    host: str = "127.0.0.1"
    port: int | None = None
    done_days: int = 14
    auth: str = "token"
    public_url: str | None = None
    sign_in_limit: int = 10
    proxy_hops: int = 0
    idle_timeout: int = 14 * 86400


@dataclass(frozen=True)
class RunningBoard:
    server: ThreadingHTTPServer
    output: io.StringIO
    errors: io.StringIO

    @property
    def state(self) -> BoardState:
        state: BoardState = self.server.RequestHandlerClass.state  # type: ignore[attr-defined]
        return state

    def request(self, method: str, path: str, headers: dict[str, str]) -> Response:
        """A request to the address and port the board is bound to."""
        address, port = self.server.server_address[:2]
        return send_request((str(address), port), method, path, headers)


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port: int = probe.getsockname()[1]
        return port


def second_loopback() -> str:
    """127.0.0.2, a loopback address other than the default one; skip where it is none.

    Linux routes all of 127.0.0.0/8 to the loopback interface; macOS only 127.0.0.1.
    """
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.2", 0))
        except OSError:
            pytest.skip("127.0.0.2 is not a loopback address here")
    return "127.0.0.2"


def board_workspace(root: Path) -> Path:
    """The team workspace, its shop repository with an item closed five days ago."""
    workspace = team_workspace(root)
    day = (datetime.now(UTC).astimezone() - timedelta(days=5)).date().isoformat()
    (workspace / "shop" / "TODO_LOG.md").write_text(
        f"# TODO Log\n\n## {day[:4]}\n\n### {day[:7]}\n\n"
        f"- [x] {day} — **General:** {CLOSED}\n  - Evidence: it ran\n"
    )
    return workspace


def add_table(workspace: Path, text: str) -> None:
    """Append tables to the workspace's local file."""
    local = workspace / "tadu-workspace.local.toml"
    local.write_text(local.read_text() + "\n" + text)


def refuse_to_serve(monkeypatch: pytest.MonkeyPatch) -> None:
    """A board that should not start fails the test instead of serving forever."""

    def serve(_server: ThreadingHTTPServer, _poll_interval: float = 0.5) -> None:
        msg = "the board started"
        raise AssertionError(msg)

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", serve)


@contextmanager
def running_board(
    argv: list[str], *, github: FakeGithub, monkeypatch: pytest.MonkeyPatch
) -> Iterator[RunningBoard]:
    """`tadu board ...` serving in a thread, its GitHub the fake; stopped on exit."""
    servers: list[ThreadingHTTPServer] = []
    serve = ThreadingHTTPServer.serve_forever

    def record(server: ThreadingHTTPServer, _poll_interval: float = 0.5) -> None:
        servers.append(server)
        serve(server, 0.01)

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", record)
    fake = functools.partial(GithubSignIn, web_url=github.url, api_url=f"{github.url}/api")
    monkeypatch.setattr("tadu.prepare_team_board.GithubSignIn", fake)
    monkeypatch.setenv("TADU_GITHUB_CLIENT_ID", "client-1")
    monkeypatch.setenv("TADU_GITHUB_CLIENT_SECRET", SECRET)
    output, errors = io.StringIO(), io.StringIO()
    monkeypatch.setattr(sys, "stdout", output)
    monkeypatch.setattr(sys, "stderr", errors)
    codes: list[int] = []
    thread = threading.Thread(target=lambda: codes.append(main(["board", *argv])), daemon=True)
    thread.start()
    deadline = time.monotonic() + 5
    while not servers and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.005)
    assert servers, f"the board did not start: {codes} {errors.getvalue()}"
    try:
        yield RunningBoard(servers[0], output, errors)
    finally:
        servers[0].shutdown()
        thread.join()
    assert codes == [0]


def check_cards(payload: dict[str, list[dict[str, str]]], expected: Settings) -> None:
    """The workspace's items, and the closed one only inside the done window."""
    titles = [card["title"] for card in payload["cards"]]
    assert "shop item." in titles
    assert any(CLOSED in title for title in titles) == (expected.done_days >= 5)
