from pathlib import Path

from tadu.instruction_file import instruction_file


def test_prefers_agents_md(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("")
    (tmp_path / "CLAUDE.md").write_text("")
    assert instruction_file(tmp_path, None) == tmp_path / "AGENTS.md"


def test_explicit_wins(tmp_path: Path) -> None:
    assert instruction_file(tmp_path, "docs/x.md") == tmp_path / "docs/x.md"


def test_none_when_absent(tmp_path: Path) -> None:
    assert instruction_file(tmp_path, None) is None


def test_file_holding_the_block_wins(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("<!-- BEGIN:nextjs-agent-rules -->\n")
    (tmp_path / "CLAUDE.md").write_text("<!-- tadu:rule v3 -->\n<!-- /tadu:rule -->\n")
    assert instruction_file(tmp_path, None) == tmp_path / "CLAUDE.md"


def test_claude_md_alone(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("")
    assert instruction_file(tmp_path, None) == tmp_path / "CLAUDE.md"
