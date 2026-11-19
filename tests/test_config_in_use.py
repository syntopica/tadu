"""Config files as people meet them: output, help, the board, and MCP tools."""

import json
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest
from team_workspace import team_workspace

from tadu.cli import main
from tadu.config_settings import CONFIG_OPTIONS
from tadu.mcp_call import mcp_call
from tadu.mcp_scope import McpScope
from tadu.parse_command_line import parse_command_line


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    (tmp_path / "TODO.md").write_text("- [ ] Pick.\n\n  Priority: high\n\n- [ ] Later.\n")
    return tmp_path


def test_output_follows_the_file_and_the_flags_override_it(
    repo: Path, user_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    user_file.write_text("version = 1\n[list]\njson = true\nlimit = 1\n")
    assert main(["list", str(repo)]) == 0
    (line,) = capsys.readouterr().out.splitlines()
    assert json.loads(line)["title"] == "Pick."
    assert main(["list", str(repo), "--no-json", "--limit", "0"]) == 0
    assert capsys.readouterr().out.count("\n") == 2
    assert main(["--no-config", "list", str(repo)]) == 0
    assert not capsys.readouterr().out.startswith("{")


def test_mcp_tools_ignore_config_files(repo: Path, user_file: Path) -> None:
    user_file.write_text("version = 1\n[defaults]\njson = true\nlimit = 1\n")
    result = mcp_call("list", {}, McpScope((str(repo),), None), main)
    content = result["content"]
    assert isinstance(content, list)
    assert content[0]["text"].splitlines()[1].endswith("- Later.")


def test_every_command_takes_the_config_options(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--help"])
    assert "--config FILE" in capsys.readouterr().out
    for command in ("list", "close", "board", "hook"):
        with pytest.raises(SystemExit):
            main([command, "--help"])
        assert "[--config FILE | --no-config]" in capsys.readouterr().out


@pytest.mark.parametrize("command", sorted(CONFIG_OPTIONS))
def test_every_settable_option_is_a_flag_of_its_command(command: str) -> None:
    argv = {
        "similar": ["similar", "x"],
        "show": ["show", "k"],
        "sync": ["sync", "."],
        "board": ["board", "--workspace=w"],
    }
    args = vars(parse_command_line(argv.get(command, [command]), {}))
    assert set(CONFIG_OPTIONS[command]) <= set(args)


def test_a_team_board_configured_in_its_workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    servers: list[ThreadingHTTPServer] = []

    def stop(server: ThreadingHTTPServer, _poll_interval: float = 0.5) -> None:
        servers.append(server)
        raise KeyboardInterrupt

    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", stop)
    monkeypatch.setenv("TADU_GITHUB_CLIENT_ID", "Iv1.abc")
    monkeypatch.setenv("TADU_GITHUB_CLIENT_SECRET", "s3cret")
    workspace = team_workspace(tmp_path)
    local = workspace / "tadu-workspace.local.toml"
    local.write_text(
        local.read_text() + "\n[board]\nauth = 'github'\nport = 0\nproxy_hops = 1\n"
        "public_url = 'https://example.com/tadu'\n"
    )
    assert main(["board", "--workspace", str(workspace)]) == 0
    assert capsys.readouterr().out == "https://example.com/tadu/\n"
    state = servers[0].RequestHandlerClass.state  # type: ignore[attr-defined]
    assert state.github.proxy_hops == 1
    assert main(["board", "--workspace", str(workspace), "--public-url", "https://t.example"]) == 0
    assert capsys.readouterr().out == "https://t.example/\n"


def test_a_view_from_a_file_is_named_when_it_is_wrong(
    tmp_path: Path, user_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "tadu-workspace.toml").write_text("version = 1\n")
    user_file.write_text("version = 1\n[list]\nview = 'mine'\n")
    assert main(["list", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err == (
        f"tadu list: unknown view mine (views: none); the view comes from {user_file}\n"
    )
    assert main(["list", "--workspace", str(tmp_path), "--view", "theirs"]) == 2
    assert capsys.readouterr().err == "tadu list: unknown view theirs (views: none)\n"
