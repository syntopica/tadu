"""Every field tadu reads in a format 1 backlog is in its task after tadu migrate."""

import json
import re
from functools import partial
from pathlib import Path

import pytest

from tadu.cli import main
from tadu.item_fields import ItemFields
from tadu.migration_tasks import migration_tasks
from tadu.read_text_exact import read_text_exact
from tadu.scan_items import scan_items

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"
EVERY_FIELD = f"""# TODO

## Billing

- [ ] Reject duplicate webhook deliveries.

  ID: {UID}

  Priority: high

  Assignees: ana, bot

  Due: 2026-11-20

  Check on: 2026-11-10

  Not before: 2026-11-05

  Labels: bug, webhooks

  Queue: ready

  Kind: task

  Estimate: 90

- [ ] Decide the retry policy.

  Kind: decision

- [!] Switch to live carrier rates.

  Waiting for the carrier. Smallest unblock: ask Ana.

  Kind: waiting

  Queue: ready

- [ ] Maybe rewrite the CLI.

  Labels: chore

  Kind: decision

  Not before: someday

  Estimate: 1h

  Queue: later

  Priority: p1

  Priority: high
"""
LOG = """# TODO Log

- [x] 2026-10-21 — Export the lock.

  ID: t-66161023-f3a9-43a3-94df-589ca752fa13
  Check on: 2026-12-01
  - Evidence: ok

- [-] 2026-10-12 — Recommend merge=union.

  Kind: later

  - Resolution: entries interleave.
"""


def held(task: dict[str, object], fields: ItemFields) -> list[str]:
    """Each field value tadu reads that the task holds neither in a key nor as a note line."""
    notes = task.get("notes", [])
    assert isinstance(notes, list)
    labels = task.get("labels", [])
    assert isinstance(labels, list)
    types = (task.get("type"), *labels)
    checks = [
        (fields.priority, task.get("priority") == fields.priority, "Priority"),
        (fields.assignees, task.get("assignees") == list(fields.assignees), "Assignees"),
        (fields.due, task.get("due") == str(fields.due), "Due"),
        (fields.labels, set(fields.labels) <= set(types), "Labels"),
        (fields.queue != "backlog", task.get("queue") == fields.queue, "Queue"),
        (fields.estimate, task.get("estimate") == fields.estimate, "Estimate"),
        (fields.not_before, task.get("defer_until") == str(fields.not_before), "Not before"),
        (fields.kind, task.get("kind") == fields.kind, "Kind"),
        (fields.check_on, task.get("check_on") == str(fields.check_on), "Check on"),
    ]
    return [
        name
        for present, stored, name in checks
        if present and not stored and not any(str(note).startswith(f"{name}: ") for note in notes)
    ]


def held_in(states: str, match: re.Match[str]) -> bool:
    return match.group(1) in states


def test_every_field_read_in_format_1_is_a_key_or_a_note_line(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(EVERY_FIELD)
    (tmp_path / "TODO_LOG.md").write_text(LOG)
    tasks, _ = migration_tasks(tmp_path)
    items = [
        item
        for name, states in (("TODO.md", " ~!"), ("TODO_LOG.md", "x-"))
        for item in scan_items(
            read_text_exact(tmp_path / name).splitlines(), "", name, partial(held_in, states)
        )
    ]
    assert len(items) == len(tasks) == 6
    assert {
        str(task["title"]): held(task, item.fields) for task, item in zip(tasks, items, strict=True)
    } == {title: [] for title in (str(task["title"]) for task in tasks)}


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        (
            0,
            {
                "type": "bug",
                "labels": ["webhooks"],
                "queue": "ready",
                "estimate": 90,
                "defer_until": "2026-11-05",
                "kind": "task",
                "check_on": "2026-11-10",
                "notes": [],
            },
        ),
        (1, {"kind": "decision", "type": "untriaged"}),
        (2, {"blocker": "Waiting for the carrier.", "kind": "waiting", "notes": ["Queue: ready"]}),
        (
            3,
            {
                "type": "chore",
                "kind": "decision",
                "priority": "p1",
                "notes": [
                    "Priority: p1",
                    "",
                    "Priority: high",
                    "",
                    "Not before: someday",
                    "",
                    "Estimate: 1h",
                    "",
                    "Queue: later",
                ],
            },
        ),
        (4, {"notes": ["Check on: 2026-12-01"], "check_on": None, "evidence": ["ok"]}),
        (5, {"kind": "later", "notes": [], "resolution": "entries interleave."}),
    ],
)
def test_each_field_lands_where_format_2_holds_it(
    tmp_path: Path, index: int, expected: dict[str, object]
) -> None:
    (tmp_path / "TODO.md").write_text(EVERY_FIELD)
    (tmp_path / "TODO_LOG.md").write_text(LOG)
    task = migration_tasks(tmp_path)[0][index]
    assert {key: task.get(key) for key in expected} == expected


def test_kinds_and_check_on_days_work_in_the_migrated_backlog(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text(EVERY_FIELD)
    assert main(["migrate", str(tmp_path), "--write"]) == 0
    assert "types" not in json.loads((tmp_path / "todo" / "tadu.json").read_text())
    capsys.readouterr()
    assert main(["list", str(tmp_path), "--kind", "decision"]) == 0
    titles = [line.split("] ", 1)[1] for line in capsys.readouterr().out.splitlines()]
    assert titles == ["- Decide the retry policy", "- Maybe rewrite the CLI"]
    assert main(["inbox", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Decide: choices a person must make" in out
    assert "[backlog/decision] - Decide the retry policy" in out
