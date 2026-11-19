"""Options left out of a command line come from the workspace's local file, then the
user's config file, then the option's own default; the command line always wins.
"""

from pathlib import Path

import pytest

from tadu.parse_command_line import parse_command_line


@pytest.fixture(autouse=True)
def outside_any_repository(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Run where no backlog is, so a configured workspace is the default scope."""
    monkeypatch.chdir(tmp_path_factory.mktemp("elsewhere"))


def workspace(root: Path, tables: str = "") -> Path:
    root.mkdir(exist_ok=True)
    (root / "tadu-workspace.toml").write_text("version = 1\n")
    (root / "tadu-workspace.local.toml").write_text("version = 1\n" + tables)
    return root


def parse(*argv: str, environ: dict[str, str] | None = None) -> dict[str, object]:
    return vars(parse_command_line(list(argv), environ or {}))


def test_without_a_file_the_declared_defaults_hold() -> None:
    args = parse("list")
    assert (args["workspace"], args["json"], args["limit"], args["done_days"]) == (
        None,
        False,
        100,
        14,
    )
    assert args["sort"] == "file"
    assert parse("similar", "x")["limit"] == 5
    board = parse("board", "--workspace", "w")
    assert (board["host"], board["port"], board["auth"], board["public_url"]) == (
        "127.0.0.1",
        None,
        "token",
        None,
    )
    assert "config" not in args
    assert "no_config" not in args


def test_each_layer_wins_over_the_one_below(tmp_path: Path, user_file: Path) -> None:
    ws = workspace(tmp_path / "ws", "[defaults]\nlimit = 3\nsort = 'due'\n[list]\nlimit = 4\n")
    user_file.write_text(
        f"version = 1\n[defaults]\nworkspace = '{ws}'\nlimit = 1\ndone_days = 2\njson = true\n"
        "sort = 'closed'\n[list]\nlimit = 2\nview = 'mine'\n"
    )
    args = parse("list")
    assert args["workspace"] == str(ws)
    assert args["limit"] == 4  # local [list] over local [defaults] over the user's file
    assert args["sort"] == "due"  # local [defaults] over the user's [defaults]
    assert (args["done_days"], args["json"], args["view"]) == (2, True, "mine")
    args = parse("list", "--limit", "9", "--no-json", "--sort", "file", "--view", "all")
    assert (args["limit"], args["json"], args["sort"], args["view"]) == (9, False, "file", "all")
    assert parse("ready")["limit"] == 3  # [defaults] reach every command with the option
    assert parse("similar", "x")["limit"] == 3


def test_the_command_lines_workspace_picks_the_local_file(tmp_path: Path, user_file: Path) -> None:
    one = workspace(tmp_path / "one", "[board]\nport = 8001\n")
    two = workspace(tmp_path / "two", "[board]\nport = 8002\nhost = '10.0.0.5'\n")
    user_file.write_text(f"version = 1\n[board]\nworkspace = '{one}'\nhost = '::1'\n")
    assert (parse("board")["port"], parse("board")["host"]) == (8001, "::1")
    other = parse("board", "--workspace", str(two))
    assert (other["port"], other["host"]) == (8002, "10.0.0.5")
    assert parse("board", "--port", "9")["port"] == 9


def test_repository_paths_on_the_command_line_beat_a_configured_workspace(
    tmp_path: Path, user_file: Path
) -> None:
    ws = workspace(tmp_path / "ws", "[list]\njson = true\n")
    user_file.write_text(f"version = 1\n[defaults]\nworkspace = '{ws}'\n")
    assert parse("list")["json"] is True
    args = parse("list", "repo")
    assert (args["workspace"], args["paths"], args["json"]) == (None, ["repo"], False)
    assert parse("show", "k", "repo")["workspace"] is None
    assert parse("doctor", "repo")["workspace"] is None


def test_a_workspace_is_relative_to_its_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "etc" / "tadu.toml"
    config.parent.mkdir()
    config.write_text("version = 1\n[board]\nworkspace = '../srv/ws'\n")
    assert parse("--config", str(config), "board")["workspace"] == str(
        tmp_path / "etc" / ".." / "srv" / "ws"
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    config.write_text("version = 1\n[board]\nworkspace = '~/ws'\n")
    assert parse("board", "--config", str(config))["workspace"] == str(tmp_path / "ws")


def test_the_file_can_be_chosen_or_left_out(tmp_path: Path, user_file: Path) -> None:
    user_file.write_text("version = 1\n[list]\nlimit = 1\n")
    named = tmp_path / "named.toml"
    named.write_text("version = 1\n[list]\nlimit = 2\n")
    assert parse("list")["limit"] == 1
    assert parse("--config", str(named), "list")["limit"] == 2
    assert parse("list", "--config", str(named))["limit"] == 2
    assert parse("list", environ={"TADU_CONFIG": str(named)})["limit"] == 2
    assert parse("--no-config", "list")["limit"] == 100
    assert parse("list", "--no-config")["limit"] == 100


def test_no_config_skips_the_local_files_tables_too(tmp_path: Path) -> None:
    ws = workspace(tmp_path / "ws", "[list]\nlimit = 7\n")
    assert parse("list", "--workspace", str(ws))["limit"] == 7
    assert parse("list", "--workspace", str(ws), "--no-config")["limit"] == 100


def test_values_are_read_as_the_command_line_reads_them(user_file: Path) -> None:
    user_file.write_text(
        "version = 1\n[board]\nworkspace = '/w'\nport = '8123'\npublic_url = 'https://Ex.com/tadu/'\n"
        "sign_in_limit = 'off'\nproxy_hops = 1\nauth = 'github'\n[init]\nformat = 2\n"
    )
    board = parse("board")
    assert (board["port"], board["public_url"], board["proxy_hops"]) == (
        8123,
        "https://ex.com/tadu",
        1,
    )
    assert board["sign_in_limit"] == ()
    assert parse("init")["format"] == "2"


@pytest.mark.parametrize("backlog", ["TODO.md", "todo/tadu.json"])
def test_inside_a_repository_its_backlog_beats_a_configured_workspace(
    tmp_path: Path, user_file: Path, monkeypatch: pytest.MonkeyPatch, backlog: str
) -> None:
    ws = workspace(tmp_path / "ws", "[list]\nlimit = 7\n")
    user_file.write_text(
        f"version = 1\n[defaults]\nworkspace = '{ws}'\njson = true\n[list]\nview = 'mine'\n"
    )
    repo = tmp_path / "repo"
    (repo / backlog).parent.mkdir(parents=True)
    (repo / backlog).write_text("")
    monkeypatch.chdir(repo)
    for command in (["list"], ["next"], ["show", "k"], ["mcp"], ["feed"]):
        assert parse(*command)["workspace"] is None, command
    assert parse("next")["json"] is True  # the rest of the file still holds
    args = parse("list")
    assert (args["view"], args["limit"]) == (None, 100)  # nor the workspace's local file
    assert parse("list", "--workspace", str(ws))["limit"] == 7
    assert parse("doctor")["workspace"] == str(ws)  # doctor has no default path
    assert parse("board")["workspace"] == str(ws)
