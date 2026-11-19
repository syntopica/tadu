"""tadu add on a TODO.md backlog keeps the options of a task backlog it has a spelling for."""

import json
from pathlib import Path

import pytest

from tadu.cli import main

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"


def test_task_backlog_options_survive_a_later_migration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["init", str(tmp_path), "--write"]) == 0
    options = ["--labels", "a, b", "--label", "c", "--assignees", "ana", "--assignee", "bot"]
    options += ["--defer-until", "2026-12-01", "--done-when", "CSV imports"]
    options += ["--done-when", "no duplicates", "--blocked-by", UID, "--note", "Context."]
    assert main(["add", str(tmp_path), "--title", "Ship importer", *options, "--write"]) == 0
    assert main(["migrate", str(tmp_path), "--write"]) == 0
    capsys.readouterr()
    task = json.loads(next((tmp_path / "todo" / "open").glob("*.json")).read_text())
    assert {key: task.get(key) for key in ("labels", "assignees", "defer_until")} == {
        "labels": ["a", "b", "c"],
        "assignees": ["ana", "bot"],
        "defer_until": "2026-12-01",
    }
    assert (task["done_when"], task["blocked_by"], task["notes"]) == (
        ["CSV imports", "", "no duplicates"],
        [UID],
        ["Context."],
    )


@pytest.mark.parametrize(
    ("options", "refusal"),
    [
        (
            ["--type", "bug", "--milestone", "m1", "--link", "https://x.test"],
            "a TODO.md backlog takes no --type, --milestone, --link",
        ),
        (
            ["--parent", UID, "--discovered-from", UID, "--related", UID, "--created-by", "ana"],
            "a TODO.md backlog takes no --parent, --discovered-from, --created-by, --related",
        ),
        (
            ["--not-before", "2026-01-01", "--defer-until", "2026-02-01"],
            "--not-before and --defer-until are the same day here; give one",
        ),
        (["--blocked-by", "t-55161023"], "--blocked-by t-55161023: give the whole task id"),
    ],
)
def test_an_option_with_no_place_in_todo_md_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], options: list[str], refusal: str
) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    assert main(["add", str(tmp_path), "--title", "Something", *options, "--write"]) == 2
    assert capsys.readouterr().err.startswith(f"tadu add: {refusal}")
    assert (tmp_path / "TODO.md").read_text() == "# TODO\n"
