"""A board on a fixed port of 127.0.0.1 that a test stops and starts again, as an
operator restarts one: sessions and ids persist in the workspace between runs.
"""

import secrets
import socket
import threading
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from fake_github import FakeGithub

from tadu.allowed_hosts import allowed_hosts
from tadu.board_memory import board_memory
from tadu.board_state import BoardState
from tadu.cli import main
from tadu.make_board_handler import make_board_handler
from tadu.sign_in_settings import IDLE_TIMEOUT_SECONDS


class LiveBoard:
    """A team board when given the fake GitHub, else a token board (a new token each run).

    `path` serves it in a subfolder, such as `/tadu`; sessions end after `idle_timeout` seconds unused.
    """

    def __init__(
        self, workspace: Path, github: FakeGithub | None, path: str = "", *, idle_timeout: int = 0
    ) -> None:
        self.workspace, self.github, self.path = workspace, github, path
        self.idle_timeout = idle_timeout or IDLE_TIMEOUT_SECONDS
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            self.port: int = probe.getsockname()[1]
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None
        self.token = ""

    @property
    def url(self) -> str:
        """The page's address; a token board's carries its token."""
        base = f"http://127.0.0.1:{self.port}{self.path}/"
        return base if self.github is not None else f"{base}?token={self.token}"

    def start(self) -> None:
        """Serve, reading the sessions and ids the workspace holds now."""
        sign_in = None
        if self.github is not None:
            pins, sessions = board_memory(str(self.workspace), self.idle_timeout)
            public = f"http://127.0.0.1:{self.port}{self.path}"
            sign_in = replace(self.github.sign_in(public), pins=pins, sessions=sessions)
        self.token = secrets.token_urlsafe(16)
        hosts = allowed_hosts("127.0.0.1", self.port)
        state = BoardState(self.workspace, 14, self.token, hosts, "read", main, sign_in)
        self.server = ThreadingHTTPServer(("127.0.0.1", self.port), BaseHTTPRequestHandler)
        self.server.RequestHandlerClass = make_board_handler(state)
        self.thread = threading.Thread(target=self.server.serve_forever, args=(0.01,), daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop serving: the port refuses connections until the next start."""
        if self.server is not None and self.thread is not None:
            self.server.shutdown()
            self.server.server_close()
            self.thread.join()
            self.server = None
