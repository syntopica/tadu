from pathlib import Path

import pytest

from tadu.agent_file import agent_file
from tadu.cli import main
from tadu.run_sync import run_sync


def test_cursor_rule_is_created_with_front_matter_that_always_applies(tmp_path: Path) -> None:
    assert main(["sync", str(tmp_path), "--agent", "cursor", "--write"]) == 0
    text = (tmp_path / ".cursor/rules/tadu.mdc").read_text()
    assert text.startswith("---\nalwaysApply: true\n---\n\n<!-- tadu:rule v5 -->\n")
    assert not (tmp_path / "AGENTS.md").exists()
    assert main(["sync", str(tmp_path), "--agent", "cursor"]) == 0


def test_an_agent_file_keeps_what_it_holds(tmp_path: Path) -> None:
    (tmp_path / "GEMINI.md").write_text("# Gemini\n")
    assert run_sync(str(tmp_path), "GEMINI.md", write=True, adopt_legacy=False) == 0
    assert (tmp_path / "GEMINI.md").read_text().startswith("# Gemini\n\n<!-- tadu:rule v5 -->\n")


def test_a_dry_run_creates_no_folder(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sync", str(tmp_path), "--agent", "copilot"]) == 0
    assert not (tmp_path / ".github").exists()
    assert "+++ " + str(tmp_path / ".github/copilot-instructions.md") in capsys.readouterr().out


def test_file_and_agent_together_are_refused(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(["sync", str(tmp_path), "--file", "X.md", "--agent", "gemini", "--write"])
    assert list(tmp_path.iterdir()) == []


def test_the_agent_wins_over_a_configured_file() -> None:
    assert agent_file("CLAUDE.md", "gemini") == "GEMINI.md"
    assert agent_file("CLAUDE.md", None) == "CLAUDE.md"


def test_a_folder_that_cannot_be_made_is_reported(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".github").write_text("not a folder\n")
    assert main(["sync", str(tmp_path), "--agent", "copilot", "--write"]) == 2
    assert "not written" in capsys.readouterr().err
