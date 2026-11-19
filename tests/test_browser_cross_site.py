"""In a real browser: a page on another port of the board's host, which is the same site
and so gets the session cookie along, cannot sign the person out or load their cards.
"""

import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import TYPE_CHECKING, ClassVar, override

import pytest
from browser_steps import BOARD_TEXT, sign_in
from live_board import LiveBoard

if TYPE_CHECKING:
    from playwright.sync_api import BrowserContext

pytestmark = pytest.mark.browser

ATTACK = """<!DOCTYPE html><title>Sibling</title><script>
const board = "http://127.0.0.1:{port}{path}";
const asked = [
  fetch(board + "/auth/logout", {{ method: "POST", mode: "no-cors", credentials: "include" }}),
  fetch(board + "/api/session", {{ method: "POST", mode: "no-cors", credentials: "include" }}),
  fetch(board + "/api/cards", {{ mode: "no-cors", credentials: "include" }}),
];
Promise.allSettled(asked).then(() => {{ document.title = "Done"; }});
</script>"""


class SiblingPage(BaseHTTPRequestHandler):
    page: ClassVar[bytes]

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(self.page)

    @override
    def log_message(self, format: str, *args: object) -> None:
        """Quiet."""


@pytest.fixture
def sibling(live_team_board: LiveBoard) -> Iterator[str]:
    """A page of another origin on the same host: same site, other port."""
    page = ATTACK.format(port=live_team_board.port, path=live_team_board.path).encode()
    server = ThreadingHTTPServer(("127.0.0.1", 0), type("Bound", (SiblingPage,), {"page": page}))
    thread = threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()
    server.server_close()
    thread.join()


def test_a_sibling_page_cannot_sign_out_or_read(
    live_team_board: LiveBoard, browser_context: "BrowserContext", sibling: str
) -> None:
    board = browser_context.new_page()
    sign_in(board, live_team_board.url)
    requests: list[tuple[str, int]] = []
    attack = browser_context.new_page()
    attack.on("response", lambda answer: requests.append((answer.url, answer.status)))
    attack.goto(sibling)
    attack.wait_for_function("document.title === 'Done'")
    statuses = {
        url.rpartition("/")[2]: status
        for url, status in requests
        if "/auth/" in url or "/api/" in url
    }
    assert set(statuses.values()) <= {0, 403}, statuses  # opaque, or refused
    board.reload()
    board.get_by_text(BOARD_TEXT).first.wait_for()  # still signed in
