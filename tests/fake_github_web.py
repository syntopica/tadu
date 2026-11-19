"""The fake GitHub with its web side, for a real browser: the consent page approves at
once, as whoever the test names, and sends the browser back to the board.
"""

import itertools
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import override
from urllib.parse import parse_qs, urlencode

from fake_github import FakeGithub, FakeHandler

SERIALS = itertools.count()


class WebHandler(FakeHandler):
    """GET /login/oauth/authorize redirects to the redirect_uri with a code for `approving`,
    bound to the request's PKCE challenge.
    """

    approving: list[str]

    @override
    def do_GET(self) -> None:
        path, _, query = self.path.partition("?")
        if path != "/login/oauth/authorize":
            super().do_GET()
            return
        asked = {name: values[0] for name, values in parse_qs(query).items()}
        code = f"code-{self.approving[0]}~{next(SERIALS)}"
        self.github.challenges[code] = asked["code_challenge"]
        back = asked["redirect_uri"] + "?" + urlencode({"code": code, "state": asked["state"]})
        self.reply(302, b"", ("Location", back))


@contextmanager
def fake_github_web(readable: dict[str, set[str]]) -> Iterator[tuple[FakeGithub, list[str]]]:
    """The fake and the login its consent page approves as (set `[0]`; the first by default)."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), BaseHTTPRequestHandler)
    github = FakeGithub(f"http://127.0.0.1:{server.server_address[1]}", readable)
    approving = [next(iter(readable))]
    fields = {"github": github, "approving": approving}
    server.RequestHandlerClass = type("BoundWeb", (WebHandler,), fields)
    thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
    thread.start()
    try:
        yield github, approving
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
