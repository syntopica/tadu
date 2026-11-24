from pathlib import Path

import pytest


@pytest.mark.parametrize("name", ["rule_block_v5.md", "rule_block_v5_tasks.md"])
def test_rule_starts_backlog_consultation_with_the_bounded_briefing(name: str) -> None:
    text = (Path(__file__).resolve().parents[1] / "tadu" / name).read_text()
    assert "tadu prime ." in text
    assert "--compact" in text
    assert "review does not authorize" in text
