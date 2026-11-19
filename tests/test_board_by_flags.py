"""`tadu board` set by flags alone, with no config file anywhere."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path

import pytest
from board_checks import check_board
from board_run import RunningBoard, Settings, board_workspace, free_port, second_loopback

from tadu.cli import main
from tadu.workspace_port import workspace_port

Start = Callable[[list[str]], AbstractContextManager[RunningBoard]]
PUBLIC_URLS = ["https://tadu.example.com", "https://mytadu.example", "https://example.com/tadu"]


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    return board_workspace(tmp_path)


def test_only_the_workspace(workspace: Path, start_board: Start) -> None:
    with start_board(["--workspace", str(workspace)]) as board:
        check_board(board, Settings(workspace))
        derived = workspace_port(str(workspace))
        port = board.server.server_address[1]
        assert port == derived or f"port {derived} is busy" in board.errors.getvalue()


def test_a_token_board_with_every_flag(workspace: Path, start_board: Start) -> None:
    port = free_port()
    argv = ["--workspace", str(workspace), "--host", "localhost", "--port", str(port)]
    with start_board([*argv, "--done-days", "3", "--auth", "token"]) as board:
        check_board(board, Settings(workspace, "localhost", port, done_days=3))


@pytest.mark.parametrize("public_url", PUBLIC_URLS)
def test_a_team_board_with_every_flag(workspace: Path, start_board: Start, public_url: str) -> None:
    port = free_port()
    argv = [
        *("--workspace", str(workspace), "--host", "localhost", "--port", str(port)),
        *("--done-days", "3", "--auth", "github", "--public-url", public_url),
        *("--sign-in-limit", "4/minute", "--proxy-hops", "1", "--idle-timeout", "30m"),
    ]
    expected = Settings(workspace, "localhost", port, 3, "github", public_url, 4, 1, 1800)
    with start_board(argv) as board:
        check_board(board, expected)


def test_a_team_board_with_only_the_flags_it_needs(workspace: Path, start_board: Start) -> None:
    with start_board(["--workspace", str(workspace), "--auth", "github", "--port", "0"]) as board:
        check_board(board, Settings(workspace, auth="github"))


@pytest.mark.usefixtures("refusing")
@pytest.mark.parametrize(
    ("flags", "message"),
    [
        (["--public-url", "https://b.example"], "tadu board: --public-url needs --auth github\n"),
        (["--sign-in-limit", "off"], "tadu board: --sign-in-limit needs --auth github\n"),
        (["--proxy-hops", "1"], "tadu board: --proxy-hops needs --auth github\n"),
        (["--idle-timeout", "8h"], "tadu board: --idle-timeout needs --auth github\n"),
    ],
)
def test_github_flags_need_github_sign_in(
    workspace: Path, capsys: pytest.CaptureFixture[str], flags: list[str], message: str
) -> None:
    assert main(["board", "--workspace", str(workspace), *flags]) == 2
    assert capsys.readouterr().err == message


def test_the_host_flag_binds_that_address(workspace: Path, start_board: Start) -> None:
    host = second_loopback()
    with start_board(["--workspace", str(workspace), "--host", host, "--port", "0"]) as board:
        check_board(board, Settings(workspace, host))
    argv = ["--workspace", str(workspace), "--host", host, "--auth", "github", "--port", "0"]
    with start_board(argv) as board:
        check_board(board, Settings(workspace, host, auth="github"))
