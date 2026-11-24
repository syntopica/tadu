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


def test_agents_md_wins_even_when_claude_holds_the_block(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("<!-- BEGIN:nextjs-agent-rules -->\n")
    (tmp_path / "CLAUDE.md").write_text("<!-- tadu:rule v5 -->\n<!-- /tadu:rule -->\n")
    assert instruction_file(tmp_path, None) == tmp_path / "AGENTS.md"


def test_agents_override_wins(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.override.md").write_text("# Override\n")
    (tmp_path / "AGENTS.md").write_text("# Standard\n")
    assert instruction_file(tmp_path, None) == tmp_path / "AGENTS.override.md"


def test_claude_md_alone(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("")
    assert instruction_file(tmp_path, None) == tmp_path / "CLAUDE.md"


def test_empty_override_does_not_shadow_the_agents_rules(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.override.md").write_text("")
    (tmp_path / "AGENTS.md").write_text("# Rules\n")
    assert instruction_file(tmp_path, None) == tmp_path / "AGENTS.md"
