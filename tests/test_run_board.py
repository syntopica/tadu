from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from board_workspace import board_workspace

from tadu.cli import main


def interrupt(_server: ThreadingHTTPServer, _poll_interval: float = 0.5) -> None:
    raise KeyboardInterrupt


def test_prints_url_and_stops_on_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", interrupt)
    assert main(["board", "--workspace", str(board_workspace(tmp_path))]) == 0
    captured = capsys.readouterr()
    url = captured.out.strip()
    assert url.startswith("http://127.0.0.1:")
    assert len(url.partition("?token=")[2]) >= 43
    assert captured.err == ""


def test_other_host_warns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", interrupt)
    workspace = str(board_workspace(tmp_path))
    assert main(["board", "--workspace", workspace, "--host", "0.0.0.0"]) == 0  # noqa: S104
    assert "reachable from other machines" in capsys.readouterr().err
    assert main(["board", "--workspace", workspace, "--host", "localhost"]) == 0
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

    monkeypatch.setattr("tadu.run_board.ThreadingHTTPServer", refuse)
    workspace = str(board_workspace(tmp_path))
    assert main(["board", "--workspace", workspace, "--port", "8123"]) == 2
    captured = capsys.readouterr()
    assert captured.err == (
        "tadu board: cannot listen on 127.0.0.1:8123: [Errno 48] Address already in use\n"
    )
    assert captured.out == ""
