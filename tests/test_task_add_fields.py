"""tadu add on a task backlog keeps every option it is given, or refuses."""

import json
from pathlib import Path

import pytest
from task_backlog import task_backlog

from tadu.cli import main


def added(root: Path) -> dict[str, object]:
    task: dict[str, object] = json.loads(next((root / "todo" / "open").glob("*.json")).read_text())
    return task


def test_kind_check_on_and_the_format_1_spellings_are_kept(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [])
    options = ["--kind", "decision", "--check-on", "2026-12-01", "--not-before", "2026-11-25"]
    options += ["--labels", "db, infra", "--label", "db", "--assignees", "ana,bot"]
    assert main(["add", str(root), "--title", "Pick a database", *options, "--write"]) == 0
    capsys.readouterr()
    task = added(root)
    assert {key: task[key] for key in ("kind", "check_on", "defer_until")} == {
        "kind": "decision",
        "check_on": "2026-12-01",
        "defer_until": "2026-11-25",
    }
    assert (task["labels"], task["assignees"]) == (["db", "infra"], ["ana", "bot"])


@pytest.mark.parametrize(
    ("options", "refusal"),
    [
        (["--no-id"], "a task backlog takes no --no-id"),
        (
            ["--not-before", "2026-01-01", "--defer-until", "2026-02-01"],
            "--not-before and --defer-until are the same day here; give one",
        ),
        (["--check-on", "tomorrow"], "refused, the task would be invalid: check_on must be a"),
    ],
)
def test_an_option_the_task_cannot_hold_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], options: list[str], refusal: str
) -> None:
    root = task_backlog(tmp_path, [])
    assert main(["add", str(root), "--title", "Something", *options, "--write"]) == 2
    assert capsys.readouterr().err.startswith(f"tadu add: {refusal}")
    assert not (root / "todo" / "open").exists()


def test_the_same_day_twice_is_one_day(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = task_backlog(tmp_path, [])
    days = ["--not-before", "2026-01-01", "--defer-until", "2026-01-01"]
    assert main(["add", str(root), "--title", "Something", *days, "--write"]) == 0
    capsys.readouterr()
    assert added(root)["defer_until"] == "2026-01-01"
