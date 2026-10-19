from pathlib import Path

from tadu.holds_rule_markers import holds_rule_markers


def test_marked_unmarked_and_unreadable(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("<!-- tadu:rule v3 -->\n")
    (tmp_path / "b.md").write_text("# B\n")
    (tmp_path / "c.md").write_bytes(b"\xff")
    assert holds_rule_markers(tmp_path / "a.md")
    assert not holds_rule_markers(tmp_path / "b.md")
    assert not holds_rule_markers(tmp_path / "c.md")
