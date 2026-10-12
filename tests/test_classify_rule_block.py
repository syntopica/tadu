from pathlib import Path

from tadu.classify_rule_block import classify_rule_block
from tadu.rule_block_text import rule_block_text

PATH = Path("AGENTS.md")


def test_current_block_is_clean() -> None:
    assert classify_rule_block(PATH, rule_block_text()) == ()


def test_legacy_heading_is_r002() -> None:
    text = "## Continuous TODO, Work Log\nold\n"
    assert [f.code for f in classify_rule_block(PATH, text)] == ["R002"]


def test_no_rule_is_r003() -> None:
    assert [f.code for f in classify_rule_block(PATH, "# A\n")] == ["R003"]


def test_older_version_is_r004() -> None:
    text = "<!-- tadu:rule v0 -->\nold\n<!-- /tadu:rule -->\n"
    assert [f.code for f in classify_rule_block(PATH, text)] == ["R004"]
