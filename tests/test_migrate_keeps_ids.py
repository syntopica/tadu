"""Every `ID:` tadu reads in a format 1 backlog is the id of its task after tadu migrate."""

import json
from pathlib import Path

import pytest

from tadu.cli import main
from tadu.read_open_items import read_open_items
from tadu.read_v1_continuation import read_v1_continuation

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"


def task_files(root: Path) -> dict[str, dict[str, object]]:
    """Every migrated task by the stem of its file."""
    return {
        path.stem: json.loads(path.read_text())
        for path in sorted((root / "todo").rglob("t-*.json"))
    }


def test_a_closed_item_keeps_its_id_and_what_depends_on_it_still_finds_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["init", str(tmp_path), "--write"]) == 0
    assert main(["add", str(tmp_path), "--title", "Fix the header", "--write"]) == 0
    fixed = read_open_items(tmp_path, ".", "")[0].fields.id
    assert fixed is not None
    depends = f"Depends on: {fixed}"
    assert main(["add", str(tmp_path), "--title", "Ship it", "--note", depends, "--write"]) == 0
    shipped = read_open_items(tmp_path, ".", "")[1].fields.id
    assert shipped is not None
    close = ["close", str(tmp_path), "--match", "Fix the header", "--evidence", "tests pass"]
    assert main([*close, "--result", "The logo shows", "--write"]) == 0
    assert f"  ID: {fixed}\n  - Result: The logo shows\n" in (tmp_path / "TODO_LOG.md").read_text()
    assert main(["migrate", str(tmp_path), "--write"]) == 0
    tasks = task_files(tmp_path)
    assert sorted(tasks) == sorted([fixed, shipped])
    closed = tasks[fixed]
    assert (closed["state"], closed["result"], closed["evidence"]) == (
        "done",
        "The logo shows",
        ["tests pass"],
    )
    assert "notes" not in closed
    assert tasks[shipped]["blocked_by"] == [fixed]
    capsys.readouterr()
    assert main(["doctor", str(tmp_path)]) == 0
    assert "J012" not in capsys.readouterr().out


def test_a_field_starting_a_paragraph_is_read_whatever_follows_it() -> None:
    parts = read_v1_continuation(
        ("", f"  ID: {UID}", "  - Evidence: tests pass", "", "  Priority: high", "  Later text.")
    )
    assert parts.fields == {"ID": UID, "Priority": "high"}
    assert parts.bullets == {"Evidence": ["tests pass"]}
    assert parts.notes == ["Later text."]


def test_a_field_line_that_does_not_start_a_paragraph_stays_text_as_doctor_reads_it() -> None:
    parts = read_v1_continuation(
        ("", "  Some text first.", f"  ID: {UID}", "", f"  ID: {UID}", "  Priority: high")
    )
    assert parts.fields == {"ID": UID}
    assert parts.notes == ["Some text first.", f"ID: {UID}", "", "Priority: high"]


def test_an_item_a_stopped_close_left_open_is_closed_first(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text(f"# TODO\n\n- [ ] Fix it.\n\n  ID: {UID}\n")
    (tmp_path / "TODO_LOG.md").write_text(
        f"# TODO Log\n\n- [x] 2026-10-10 — Fix it.\n\n  ID: {UID}\n  - Evidence: ok\n"
    )
    assert main(["migrate", str(tmp_path), "--write"]) == 2
    assert "TODO.md:5: an item is also closed in TODO_LOG.md (doctor's T005)" in (
        capsys.readouterr().err
    )
    assert not (tmp_path / "todo").exists()
