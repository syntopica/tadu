import socket

import pytest

from tadu.bind_board_server import bind_board_server


def busy_port() -> tuple[socket.socket, int]:
    holder = socket.socket()
    holder.bind(("127.0.0.1", 0))
    holder.listen()
    return holder, holder.getsockname()[1]


def test_binds_the_port_asked_for() -> None:
    holder, port = busy_port()
    holder.close()
    with bind_board_server("127.0.0.1", port, fallback=False) as server:
        assert server.server_address[1] == port


def test_busy_port_falls_back_to_any_free_port(capsys: pytest.CaptureFixture[str]) -> None:
    holder, port = busy_port()
    with holder, bind_board_server("127.0.0.1", port, fallback=True) as server:
        assert server.server_address[1] not in (0, port)
    assert capsys.readouterr().err == f"tadu board: port {port} is busy; using any free port\n"


def test_busy_port_without_fallback_raises() -> None:
    holder, port = busy_port()
    with holder, pytest.raises(OSError, match="in use"):
        bind_board_server("127.0.0.1", port, fallback=False)
