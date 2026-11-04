import io
from typing import TYPE_CHECKING, cast

from tadu.send_board_response import send_board_response

if TYPE_CHECKING:
    from http.server import BaseHTTPRequestHandler


class Recorder:
    def __init__(self, command: str) -> None:
        self.command = command
        self.sent: list[object] = []
        self.wfile = io.BytesIO()

    def send_response(self, status: int) -> None:
        self.sent.append(status)

    def send_header(self, name: str, value: str) -> None:
        self.sent.append((name, value))

    def end_headers(self) -> None:
        self.sent.append("end")


def test_headers_then_body() -> None:
    recorder = Recorder("GET")
    handler = cast("BaseHTTPRequestHandler", recorder)
    send_board_response(handler, (200, b"hi", "text/plain"), ("X-A", "1"))
    assert recorder.sent == [
        200,
        ("Content-Type", "text/plain"),
        ("Content-Length", "2"),
        ("X-A", "1"),
        "end",
    ]
    assert recorder.wfile.getvalue() == b"hi"


def test_head_gets_no_body() -> None:
    recorder = Recorder("HEAD")
    send_board_response(cast("BaseHTTPRequestHandler", recorder), (405, b"no", "text/plain"))
    assert recorder.wfile.getvalue() == b""
    assert ("Content-Length", "2") in recorder.sent
