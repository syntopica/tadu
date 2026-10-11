from pathlib import Path

from tadu.check_rule_block import check_rule_block
from tadu.rule_block_text import rule_block_text


def test_current_block_passes(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Agents\n\n" + rule_block_text())
    assert check_rule_block(tmp_path) == ()


def test_legacy_section_is_r002(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("## Continuous TODO, Work Log\n\nold text\n")
    assert [f.code for f in check_rule_block(tmp_path)] == ["R002"]


def test_nothing_is_r003(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# Agents\n")
    assert [f.code for f in check_rule_block(tmp_path)] == ["R003"]


def test_no_instruction_file_is_r001(tmp_path: Path) -> None:
    assert [f.code for f in check_rule_block(tmp_path)] == ["R001"]


def test_open_without_close_is_r005(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("<!-- tadu:rule v1 -->\nbody\n")
    assert [f.code for f in check_rule_block(tmp_path)] == ["R005"]


def test_close_before_open_is_r005(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("<!-- /tadu:rule -->\n<!-- tadu:rule v1 -->\n")
    assert [f.code for f in check_rule_block(tmp_path)] == ["R005"]


def test_old_block_is_r004(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("<!-- tadu:rule v0 -->\nx\n<!-- /tadu:rule -->\n")
    assert [f.code for f in check_rule_block(tmp_path)] == ["R004"]


def test_two_opening_markers_are_r005(tmp_path: Path) -> None:
    block = rule_block_text()
    (tmp_path / "AGENTS.md").write_text(block + "\n" + block)
    assert [f.code for f in check_rule_block(tmp_path)] == ["R005"]


def test_inline_mention_of_the_markers_is_r003_not_a_block(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("Wrap the rule in `<!-- tadu:rule v1 -->` lines.\n")
    assert [f.code for f in check_rule_block(tmp_path)] == ["R003"]


def test_fenced_example_next_to_a_real_block_passes(tmp_path: Path) -> None:
    fenced = "```md\n<!-- tadu:rule v0 -->\nx\n<!-- /tadu:rule -->\n```\n"
    (tmp_path / "AGENTS.md").write_text(fenced + rule_block_text())
    assert check_rule_block(tmp_path) == ()


def test_crlf_block_passes(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_bytes(rule_block_text().replace("\n", "\r\n").encode())
    assert check_rule_block(tmp_path) == ()
