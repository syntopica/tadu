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
