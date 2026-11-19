from datetime import UTC, datetime

from tadu.log_runs import log_runs
from tadu.loose_text_task import loose_text_task
from tadu.task_problems import task_problems

SAID = "the log records no state, result or evidence for it, so it is closed as done."


def first_note(task: dict[str, object]) -> str:
    notes = task["notes"]
    assert isinstance(notes, list)
    return str(notes[0])


def test_a_dated_block_of_the_log_is_a_closed_task_holding_it() -> None:
    lines = ["### 2025-06-03 — Rotated the keys", "", "Done by Ana."]
    task = loose_text_task("TODO_LOG.md", 19, lines, "2025-06-03")
    assert (task["title"], task["state"], task["closed"], task["result"]) == (
        "Rotated the keys",
        "done",
        "2025-06-03",
        "Rotated the keys",
    )
    assert task["notes"] == [
        f"Migrated from TODO_LOG.md line 20, written outside its dated entries; {SAID}",
        "",
        *lines,
    ]
    assert task_problems(task) == ()


def test_what_the_log_does_not_say_is_said_in_the_notes() -> None:
    month = loose_text_task("TODO_LOG.md", 0, ["Moved billing. Checked nightly."], "2025-05")
    assert (month["title"], month["closed"]) == ("Moved billing. Checked nightly", "2025-05-01")
    assert first_note(month).endswith("in the month 2025-05, so it is closed on 2025-05-01.")
    year = loose_text_task("TODO_LOG.md", 0, ["### A heading without a day"], "2024")
    assert (year["title"], year["closed"]) == ("A heading without a day", "2024-01-01")
    undated = loose_text_task("TODO_LOG.md", 0, ["- * -", "Some text."], None)
    assert undated["title"] == "Some text"
    assert undated["closed"] == datetime.now(UTC).date().isoformat()
    assert first_note(undated).endswith("so it is closed on the day it was migrated.")
    assert loose_text_task("TODO_LOG.md", 0, ["###"], None)["title"] == "Loose text"


def test_a_block_of_todo_md_is_an_open_task_to_sort() -> None:
    task = loose_text_task("TODO.md", 6, ["### Ideas", "", "Try a cache."], None)
    assert (task["title"], task["state"], task["priority"]) == ("Ideas", "pending", "untriaged")
    assert first_note(task) == (
        "Kept from TODO.md line 7, written outside its items: no task held it when the backlog "
        "was migrated. Move it into the task it belongs to, or make it one."
    )
    assert "closed" not in task
    assert task_problems(task) == ()


def test_blocks_are_split_at_headings_and_entries_and_keep_fences() -> None:
    lines = [
        "# TODO Log",
        "## 2025",
        "### 2025-05",
        "Loose words.",
        "```",
        "- [x] 2025-05-01 — fenced, so not an entry",
        "```",
        "### Another block",
        "more",
        "- [x] 2025-05-02 — An entry.",
        "## Archive",
        "Prose of a section without entries.",
    ]
    assert log_runs(lines) == [
        (3, lines[3:7], "2025-05"),
        (7, lines[7:9], "2025-05"),
        (10, lines[10:12], "2025-05"),
    ]
