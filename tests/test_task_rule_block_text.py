from pathlib import Path

from tadu.classify_rule_block import classify_rule_block
from tadu.rule_block_text import rule_block_text
from tadu.task_rule_block_text import task_rule_block_text


def test_block_is_marked_like_the_shared_one() -> None:
    text = task_rule_block_text()
    assert text.splitlines()[0] == rule_block_text().splitlines()[0]
    assert text.endswith("<!-- /tadu:rule -->\n")
    assert classify_rule_block(Path("AGENTS.md"), text) == ()


def test_block_names_no_markdown_backlog() -> None:
    text = task_rule_block_text()
    for phrase in ("TODO.md", "TODO_LOG.md", "format 1", "spec/todo-format-v1"):
        assert phrase not in text


def test_block_teaches_the_task_commands() -> None:
    text = " ".join(task_rule_block_text().split())
    for phrase in (
        "Never edit task files by hand",
        "tadu similar",
        "tadu claim ID",
        "--duplicate-of ID",
        "blocked_by",
    ):
        assert phrase in text
