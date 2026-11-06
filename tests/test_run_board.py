from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from board_workspace import board_workspace

from tadu.cli import main
from tadu.workspace_port import workspace_port


def interrupt(_server: ThreadingHTTPServer, _poll_interval: float = 0.5) -> None:
    raise KeyboardInterrupt


def test_prints_url_and_stops_on_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", interrupt)
    assert main(["board", "--workspace", str(board_workspace(tmp_path))]) == 0
    captured = capsys.readouterr()
    url = captured.out.strip()
    port = workspace_port(tmp_path)
    if captured.err == "":
        assert url.startswith(f"http://127.0.0.1:{port}/?token=")
    else:
        assert captured.err == f"tadu board: port {port} is busy; using any free port\n"
    assert len(url.partition("?token=")[2]) >= 43


def test_other_host_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", interrupt)
    workspace = str(board_workspace(tmp_path))
    argv = ["board", "--workspace", workspace, "--port", "0"]
    assert main([*argv, "--host", "0.0.0.0"]) == 0  # noqa: S104
    captured = capsys.readouterr()
    port = captured.out.partition("0.0.0.0:")[2].partition("/")[0]
    assert captured.err == (
        "tadu board: warning: listening on 0.0.0.0; only requests whose Host header is "
        f"0.0.0.0:{port} are served\n"
    )
    assert main([*argv, "--host", "localhost"]) == 0
    assert capsys.readouterr().err == ""


def test_bad_workspace_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["board", "--workspace", str(tmp_path)]) == 2
    captured = capsys.readouterr()
    assert captured.err.startswith("tadu board: ")
    assert captured.out == ""


def test_bind_failure_exits_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def refuse(*_args: object) -> None:
        raise OSError(48, "Address already in use")

    monkeypatch.setattr("tadu.bind_board_server.ThreadingHTTPServer", refuse)
    workspace = str(board_workspace(tmp_path))
    assert main(["board", "--workspace", workspace, "--port", "8123"]) == 2
    captured = capsys.readouterr()
    assert captured.err == (
        "tadu board: cannot listen on 127.0.0.1:8123: [Errno 48] Address already in use\n"
    )
    assert captured.out == ""
