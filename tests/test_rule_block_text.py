from pathlib import Path

from tadu.check_log_file import check_log_file
from tadu.rule_block_open_pattern import RULE_BLOCK_OPEN_PATTERN
from tadu.rule_block_text import rule_block_text


def test_block_is_marked_and_ends_in_newline() -> None:
    text = rule_block_text()
    assert text.startswith("<!-- tadu:rule v3 -->\n")
    assert text.endswith("<!-- /tadu:rule -->\n")
    assert RULE_BLOCK_OPEN_PATTERN.match(text.splitlines()[0]) is not None
    assert "## Continuous TODO, Work Log, and History Coverage" in text


def test_heading_is_separated_from_the_open_marker() -> None:
    lines = rule_block_text().splitlines()
    assert lines[1] == ""
    assert lines[2].startswith("## ")


def test_log_template_in_the_block_passes_the_log_check(tmp_path: Path) -> None:
    template = rule_block_text().split("```md\n")[1].split("```")[0]
    entries = template.replace("YYYY-MM-DD", "2026-10-12")
    log = f"# TODO Log\n\n<!-- tadu:log v1 since 2026-10-01 -->\n\n## 2026\n\n### 2026-10\n\n{entries}"
    (tmp_path / "TODO_LOG.md").write_text(log)
    assert check_log_file(tmp_path) == ()


def test_block_names_the_required_labels_and_the_spec() -> None:
    text = rule_block_text()
    assert "`[x]` entry needs an `Evidence:` line" in text
    assert "`[-]` entry a\n  `Resolution:` line" in text
    assert "https://github.com/syntopica/tadu/blob/main/spec/todo-format-v1.md" in text
