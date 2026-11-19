"""A config file that cannot be used stops the command with exit 2 and says where."""

from pathlib import Path

import pytest

from tadu.cli import main


@pytest.mark.parametrize(
    ("text", "problem"),
    [
        ("[list]\nlimit = 1\n", "version must be 1"),
        ("version = 1\n[list]\nlimit = -1\n", "[list] limit: must be 0 or more: -1"),
        ("version = 1\n[list]\nlimit = 'many'\n", "[list] limit: not an integer: many"),
        ("version = 1\n[list]\nlimit = 1.5\n", "[list] limit: must be a string or a whole number"),
        ("version = 1\n[list]\nlimit = true\n", "[list] limit: must be a string or a whole number"),
        ("version = 1\n[list]\nsort = 'size'\n", "[list] sort: must be one of file, priority,"),
        ("version = 1\n[list]\njson = 'yes'\n", "[list] json: must be true or false"),
        ("version = 1\n[defaults]\njson = 1\n", "[defaults] json: must be true or false"),
        ("version = 1\n[list]\ndone-days = 3\n", "[list] done-days: a config file cannot set it"),
        ("version = 1\n[list]\nassignee = 'ana'\n", "[list] takes done_days, json, limit, sort,"),
        ("version = 1\n[defaults]\nwrite = true\n", "[defaults] write: a config file cannot set"),
        ("version = 1\nlist = 3\n", "list must be a table, [list]"),
        ("version = 1\n[close]\nwrite = true\n", "close: a config file has version, [defaults]"),
        ("version = 1\nworkspace = 'w'\n", "workspace: a config file has version"),
        ("version = 1\n[list\n", "Expected ']'"),
    ],
)
def test_a_bad_user_file(
    user_file: Path, capsys: pytest.CaptureFixture[str], text: str, problem: str
) -> None:
    user_file.write_text(text)
    assert main(["list"]) == 2
    err = capsys.readouterr().err
    assert err.startswith(f"tadu: {user_file}: ")
    assert problem in err


def test_a_dashed_key_names_the_right_spelling(
    user_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    user_file.write_text("version = 1\n[board]\npublic-url = 'https://b.example'\n")
    assert main(["board", "--workspace", "w"]) == 2
    assert capsys.readouterr().err.endswith(
        "[board] public-url: a config file cannot set it here; write public_url\n"
    )


def test_a_value_of_another_command_is_checked_when_it_runs(
    user_file: Path, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    user_file.write_text("version = 1\n[board]\npublic_url = 'board.example'\n")
    (tmp_path / "TODO.md").write_text("# TODO\n")
    assert main(["list", str(tmp_path)]) == 0
    assert main(["board", "--workspace", str(tmp_path)]) == 2
    assert "[board] public_url: must be http:// or https://" in capsys.readouterr().err


def test_the_local_file_cannot_name_a_workspace(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "tadu-workspace.toml").write_text("version = 1\n")
    local = tmp_path / "tadu-workspace.local.toml"
    local.write_text("version = 1\n[board]\nworkspace = '/elsewhere'\n")
    assert main(["board", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err == (
        f"tadu: {local}: [board] workspace: a config file cannot set it here; [board] takes "
        "auth, done_days, host, idle_timeout, port, proxy_hops, public_url, sign_in_limit\n"
    )
    local.write_text("version = 1\n[boards]\nport = 1\n")
    assert main(["board", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err == f"tadu: {local}: unknown top-level key boards\n"


def test_a_named_file_must_exist(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    missing = tmp_path / "nope.toml"
    assert main(["--config", str(missing), "list"]) == 2
    assert capsys.readouterr().err.startswith(f"tadu: {missing}: ")


def test_the_environment_names_a_file_that_must_exist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TADU_CONFIG", str(tmp_path / "nope.toml"))
    assert main(["list"]) == 2
    assert "nope.toml" in capsys.readouterr().err


def test_config_and_no_config_together(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        main(["list", "--config", "a.toml", "--no-config"])
    assert stop.value.code == 2
    assert "not allowed with argument" in capsys.readouterr().err
    assert main(["--config", "a.toml", "list", "--no-config"]) == 2
    assert capsys.readouterr().err == "tadu: give --config or --no-config, not both\n"


def test_a_board_still_needs_a_workspace(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as stop:
        main(["board"])
    assert stop.value.code == 2
    err = capsys.readouterr().err
    assert err.startswith("usage: tadu board")
    assert err.endswith("tadu board: error: the following arguments are required: --workspace\n")
