"""`tadu board` set by config files, with flags overriding them one at a time or all."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import replace
from pathlib import Path

import pytest
from board_checks import check_board
from board_run import RunningBoard, Settings, add_table, board_workspace, free_port, second_loopback

from tadu.cli import main

Start = Callable[[list[str]], AbstractContextManager[RunningBoard]]
SUBFOLDER = "https://example.com/tadu"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "a").mkdir()
    return board_workspace(tmp_path / "a")


@pytest.fixture
def configured(workspace: Path, user_file: Path) -> Settings:
    """A team board in the user's file, every setting away from its default."""
    settings = Settings(workspace, "localhost", free_port(), 3, "github", SUBFOLDER, 4, 1, 8 * 3600)
    user_file.write_text(
        f"version = 1\n[board]\nworkspace = '{workspace}'\nhost = 'localhost'\n"
        f"port = {settings.port}\ndone_days = 3\nauth = 'github'\npublic_url = '{SUBFOLDER}'\n"
        "sign_in_limit = '4/minute'\nproxy_hops = 1\nidle_timeout = '8h'\n"
    )
    return settings


def test_the_configured_board_as_is(configured: Settings, start_board: Start) -> None:
    with start_board([]) as board:
        check_board(board, configured)


@pytest.mark.parametrize(
    ("flags", "changed"),
    [
        (["--host", "127.0.0.1"], {"host": "127.0.0.1"}),
        (["--done-days", "14"], {"done_days": 14}),
        (["--public-url", "https://tadu.example.com"], {"public_url": "https://tadu.example.com"}),
        (["--public-url", "https://mytadu.example/"], {"public_url": "https://mytadu.example"}),
        (["--sign-in-limit", "2/minute"], {"sign_in_limit": 2}),
        (["--proxy-hops", "0"], {"proxy_hops": 0}),
        (["--idle-timeout", "2h"], {"idle_timeout": 7200}),
        # The command line's --auth token drops the file's GitHub settings with it.
        (["--auth", "token"], {"auth": "token", "public_url": None}),
    ],
)
def test_one_flag_overrides_one_setting(
    configured: Settings, start_board: Start, flags: list[str], changed: dict[str, object]
) -> None:
    with start_board(flags) as board:
        check_board(board, replace(configured, **changed))  # type: ignore[arg-type]


def test_the_port_and_the_workspace_flags(
    configured: Settings, start_board: Start, tmp_path: Path
) -> None:
    port = free_port()
    with start_board(["--port", str(port)]) as board:
        check_board(board, replace(configured, port=port))
    (tmp_path / "b").mkdir()
    other = board_workspace(tmp_path / "b")
    with start_board(["--workspace", str(other)]) as board:
        check_board(board, replace(configured, workspace=other))


@pytest.mark.usefixtures("configured")
def test_every_flag_at_once(start_board: Start, tmp_path: Path) -> None:
    (tmp_path / "b").mkdir()
    other, port = board_workspace(tmp_path / "b"), free_port()
    argv = [
        *("--workspace", str(other), "--host", "127.0.0.1", "--port", str(port)),
        *("--done-days", "14", "--auth", "github", "--public-url", "https://tadu.example.com"),
        *("--sign-in-limit", "2/minute", "--proxy-hops", "0", "--idle-timeout", "14d"),
    ]
    expected = Settings(other, "127.0.0.1", port, 14, "github", "https://tadu.example.com", 2, 0)
    with start_board(argv) as board:
        check_board(board, expected)


def test_the_local_file_over_the_users_and_a_flag_over_both(
    configured: Settings, start_board: Start
) -> None:
    local_port, flag_port = free_port(), free_port()
    add_table(configured.workspace, f"[board]\nport = {local_port}\nsign_in_limit = '2/minute'\n")
    with start_board([]) as board:
        check_board(board, replace(configured, port=local_port, sign_in_limit=2))
    with start_board(["--port", str(flag_port)]) as board:
        check_board(board, replace(configured, port=flag_port, sign_in_limit=2))


def test_no_config_leaves_only_the_flags(configured: Settings, start_board: Start) -> None:
    add_table(configured.workspace, "[board]\ndone_days = 1\n")
    argv = ["--no-config", "--workspace", str(configured.workspace), "--port", "0"]
    with start_board(argv) as board:
        check_board(board, Settings(configured.workspace))


def test_auth_github_overrides_a_token_board(workspace: Path, start_board: Start) -> None:
    add_table(workspace, "[board]\nauth = 'token'\ndone_days = 3\nhost = 'localhost'\n")
    with start_board(["--workspace", str(workspace), "--auth", "github", "--port", "0"]) as board:
        check_board(board, Settings(workspace, "localhost", done_days=3, auth="github"))


@pytest.mark.usefixtures("configured", "refusing")
def test_a_flag_still_needs_github_sign_in(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["board", "--auth", "token", "--public-url", "https://b.example"]) == 2
    assert capsys.readouterr().err == "tadu board: --public-url needs --auth github\n"


@pytest.mark.usefixtures("configured", "refusing")
def test_a_bad_flag_is_refused_though_the_file_is_fine(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["board", "--port", "-1"])
    assert "argument --port: must be 0 or more: -1" in capsys.readouterr().err


def test_the_host_flag_over_the_files_host(configured: Settings, start_board: Start) -> None:
    host = second_loopback()
    with start_board(["--host", host]) as board:
        check_board(board, replace(configured, host=host))
