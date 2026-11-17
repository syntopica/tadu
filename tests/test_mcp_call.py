from pathlib import Path

import pytest

from tadu.cli import main
from tadu.mcp_call import mcp_call
from tadu.mcp_scope import McpScope
from tadu.run_captured import run_captured


def text(result: dict[str, object]) -> str:
    content = result["content"]
    assert isinstance(content, list)
    return str(content[0]["text"])


def test_runs_the_command_and_keeps_its_output(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] Pick.\n\n  Kind: decision\n")
    scope = McpScope((str(tmp_path),), None)
    result = mcp_call("inbox", {}, scope, main)
    assert result["isError"] is False
    assert text(result).startswith("Decide: choices a person must make\n")
    assert text(mcp_call("next", {}, scope, main)).startswith("tadu next: nothing an agent")


def test_failures_are_tool_errors(tmp_path: Path) -> None:
    scope = McpScope((str(tmp_path / "a"), str(tmp_path / "b")), None)
    bad = mcp_call("urgent", {"days": "1"}, scope, main)
    assert (bad["isError"], text(bad)) == (True, "days must be an integer")
    two = mcp_call("add", {"title": "T"}, scope, main)
    assert two["isError"] is True
    assert text(two).startswith("several repositories; give `repository` as one of: a (")
    missing = mcp_call("show", {"key": "k"}, scope, main)
    assert missing["isError"] is True


def test_empty_output_says_so() -> None:
    result = mcp_call("next", {}, McpScope((), None), lambda _argv: 0)
    assert text(result) == "Nothing found."


def test_captured_argparse_exit(capsys: pytest.CaptureFixture[str]) -> None:
    code, output = run_captured(main, ["list", "--kind", "soon"])
    assert code == 2
    assert "invalid choice: 'soon'" in output
    assert run_captured(main, ["--version"])[0] == 0

    def exit_with_text(_argv: list[str]) -> int:
        message = "stop"
        raise SystemExit(message)

    assert run_captured(exit_with_text, []) == (2, "")
    assert capsys.readouterr() == ("", "")
