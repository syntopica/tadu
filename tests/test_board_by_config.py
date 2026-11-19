"""`tadu board` set by config files alone: no flag beyond, at most, --workspace or --config."""

from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path

import pytest
from board_checks import check_board
from board_run import RunningBoard, Settings, add_table, board_workspace, free_port, second_loopback

from tadu.cli import main

Start = Callable[[list[str]], AbstractContextManager[RunningBoard]]
PUBLIC_URLS = ["https://tadu.example.com", "https://mytadu.example", "https://example.com/tadu"]


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    return board_workspace(tmp_path)


def team_table(workspace: Path, port: int, public_url: str) -> str:
    """A [board] table of a team board with every setting away from its default."""
    return (
        f"[board]\nworkspace = '{workspace}'\nhost = 'localhost'\nport = {port}\ndone_days = 3\n"
        f"auth = 'github'\npublic_url = '{public_url}'\nsign_in_limit = '4/minute'\n"
        "proxy_hops = 1\nidle_timeout = '8h'\n"
    )


@pytest.mark.parametrize("public_url", PUBLIC_URLS)
def test_a_team_board_all_from_the_users_file(
    workspace: Path, start_board: Start, user_file: Path, public_url: str
) -> None:
    port = free_port()
    user_file.write_text("version = 1\n" + team_table(workspace, port, public_url))
    with start_board([]) as board:
        check_board(
            board, Settings(workspace, "localhost", port, 3, "github", public_url, 4, 1, 8 * 3600)
        )


def test_a_team_board_from_the_workspaces_local_file(
    workspace: Path, start_board: Start, user_file: Path
) -> None:
    port = free_port()
    user_file.write_text(f"version = 1\n[defaults]\nworkspace = '{workspace}'\n")
    add_table(
        workspace,
        f"[defaults]\ndone_days = 3\n[board]\nport = {port}\nauth = 'github'\n"
        "public_url = 'https://example.com/tadu'\nsign_in_limit = '2/minute'\nproxy_hops = 1\n",
    )
    expected = Settings(workspace, "127.0.0.1", port, 3, "github", "https://example.com/tadu", 2, 1)
    with start_board([]) as board:
        check_board(board, expected)
    with start_board(["--workspace", str(workspace)]) as board:
        check_board(board, expected)


def test_a_token_board_from_the_users_file(
    workspace: Path, start_board: Start, user_file: Path
) -> None:
    port = free_port()
    user_file.write_text(
        f"version = 1\n[board]\nworkspace = '{workspace}'\nhost = 'localhost'\nport = '{port}'\n"
        "done_days = 3\nauth = 'token'\n"
    )
    with start_board([]) as board:
        check_board(board, Settings(workspace, "localhost", port, 3))


def test_a_file_named_by_config_or_the_environment(
    workspace: Path, start_board: Start, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    port = free_port()
    named = tmp_path / "board.toml"
    named.write_text("version = 1\n" + team_table(workspace, port, "https://tadu.example.com"))
    expected = Settings(
        workspace, "localhost", port, 3, "github", "https://tadu.example.com", 4, 1, 8 * 3600
    )
    with start_board(["--config", str(named)]) as board:
        check_board(board, expected)
    monkeypatch.setenv("TADU_CONFIG", str(named))
    with start_board([]) as board:
        check_board(board, expected)


def test_defaults_reach_the_board(workspace: Path, start_board: Start, user_file: Path) -> None:
    user_file.write_text(f"version = 1\n[defaults]\nworkspace = '{workspace}'\ndone_days = 3\n")
    with start_board(["--port", "0"]) as board:
        check_board(board, Settings(workspace, done_days=3))


@pytest.mark.usefixtures("refusing")
@pytest.mark.parametrize(
    ("table", "message"),
    [
        ("[board]\npublic_url = 'https://b.example'\n", 'public_url needs auth = "github"'),
        ("[board]\nproxy_hops = 1\nauth = 'token'\n", 'proxy_hops needs auth = "github"'),
        ("[board]\nsign_in_limit = '0/minute'\n", "[board] sign_in_limit: "),
        ("[board]\nidle_timeout = '5m'\n", "[board] idle_timeout: must be a duration"),
        ("[board]\nidle_timeout = '8h'\n", 'idle_timeout needs auth = "github"'),
        ("[board]\nport = 'http'\n", "[board] port: not an integer: http"),
        ("[board]\nauth = 'oauth'\n", "[board] auth: must be one of token, github, not oauth"),
        ("[board]\nhost = true\n", "[board] host: must be a string or a whole number"),
        ("[board]\npublic_url = 'https://example.com/api'\n", "[board] public_url: must be http"),
        ("[board]\nclient_secret = 'x'\n", "[board] client_secret: a config file cannot set it"),
    ],
)
def test_a_bad_board_table_is_refused_naming_the_file(
    workspace: Path, capsys: pytest.CaptureFixture[str], table: str, message: str
) -> None:
    add_table(workspace, table)
    assert main(["board", "--workspace", str(workspace)]) == 2
    err = capsys.readouterr().err
    assert str(workspace / "tadu-workspace.local.toml") in err
    assert message in err


@pytest.mark.usefixtures("refusing")
def test_without_a_workspace_anywhere(user_file: Path, capsys: pytest.CaptureFixture[str]) -> None:
    user_file.write_text("version = 1\n[board]\nport = 8123\n")
    with pytest.raises(SystemExit):
        main(["board"])
    assert capsys.readouterr().err.endswith("the following arguments are required: --workspace\n")


def test_the_host_setting_binds_that_address(
    workspace: Path, start_board: Start, user_file: Path
) -> None:
    host = second_loopback()
    user_file.write_text(f"version = 1\n[board]\nworkspace = '{workspace}'\nhost = '{host}'\n")
    with start_board(["--port", "0"]) as board:
        check_board(board, Settings(workspace, host))
