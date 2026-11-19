"""A task close run again after it stopped between writing closed/ and deleting open/."""

import json
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main

ID = str(sample_task(1)["id"])


def stopped(tmp_path: Path, recorded: dict[str, object], opened: dict[str, object]) -> Path:
    """A backlog with the task in closed/ and still in open/, as a stopped close leaves it."""
    root = task_backlog(tmp_path, [recorded, sample_task(2)])
    (root / "todo" / "open" / f"{ID}.json").write_text(json.dumps(opened, indent=2) + "\n")
    return root


def close(root: Path, *args: str) -> int:
    return main(["close", str(root), "--id", ID, *args, "--write"])


def closed(root: Path) -> dict[str, object]:
    task: dict[str, object] = json.loads((root / "todo" / "closed" / f"{ID}.json").read_text())
    return task


def test_finishing_keeps_the_record_and_adds_new_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, sample_task(1, "done"), sample_task(1))
    assert main(["close", str(root), "--id", ID, "--evidence", "CI green"]) == 0
    assert f"would finish the stopped close of {ID} as done" in capsys.readouterr().out
    assert (root / "todo" / "open" / f"{ID}.json").exists()
    assert close(root, "--evidence", "CI green") == 0
    assert f"finished the stopped close of {ID} as done" in capsys.readouterr().out
    assert not (root / "todo" / "open" / f"{ID}.json").exists()
    task = closed(root)
    assert (task["closed"], task["result"]) == ("2026-11-01", "Done.")
    assert task["evidence"] == ["pytest passes", "CI green"]


def test_a_default_result_takes_the_one_given_and_the_same_evidence_is_kept_once(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, sample_task(1, "done", result="Task 1"), sample_task(1))
    assert close(root, "--evidence", "pytest passes", "--result", "Shipped") == 0
    capsys.readouterr()
    assert (closed(root)["result"], closed(root)["evidence"]) == ("Shipped", ["pytest passes"])


def test_a_cancelled_record_is_finished_by_the_same_resolution(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, sample_task(1, "cancelled"), sample_task(1))
    assert close(root, "--resolution", "Dropped.") == 0
    capsys.readouterr()
    assert closed(root) == sample_task(1, "cancelled")


@pytest.mark.parametrize(
    "case",
    [
        (
            sample_task(1, "done"),
            ("--resolution", "Dropped."),
            "as done; run the close again with --evidence to finish it",
        ),
        (
            sample_task(1, "cancelled"),
            ("--evidence", "e"),
            "as cancelled; run the close again with --resolution to finish it",
        ),
        (
            sample_task(1, "done"),
            ("--evidence", "e", "--result", "Other."),
            (
                "with result 'Done.'; run the close again with that result, or without one "
                "to finish it"
            ),
        ),
        (
            sample_task(1, "cancelled"),
            ("--resolution", "Superseded."),
            "with resolution 'Dropped.'; run the close again with that resolution to finish it",
        ),
        (
            sample_task(1, "cancelled"),
            ("--duplicate-of", str(sample_task(2)["id"])),
            "not as a duplicate; run the close again the same way to finish it",
        ),
        (
            sample_task(1, "cancelled", duplicate_of=str(sample_task(2)["id"])),
            ("--resolution", "Dropped."),
            (
                f"as a duplicate of {sample_task(2)['id']}; run the close again the same way "
                "to finish it"
            ),
        ),
    ],
)
def test_another_state_result_resolution_or_duplicate_is_refused(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    case: tuple[dict[str, object], tuple[str, ...], str],
) -> None:
    recorded, args, refusal = case
    root = stopped(tmp_path, recorded, sample_task(1))
    assert close(root, *args) == 2
    where = f"todo/closed/{ID}.json"
    expected = f"already closed in {where} by a close that stopped halfway, {refusal}"
    assert capsys.readouterr().err == f"tadu close: {expected}\n"
    assert (root / "todo" / "open" / f"{ID}.json").exists()
    assert closed(root) == recorded


def test_an_open_copy_changed_since_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, sample_task(1, "done"), sample_task(1, priority="high"))
    assert close(root, "--evidence", "e") == 2
    assert "and the open copy differs from it in priority; merge them by hand" in (
        capsys.readouterr().err
    )


def test_a_newer_or_unreadable_closed_copy_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, {**sample_task(1, "done"), "tadu": 3}, sample_task(1))
    assert close(root, "--evidence", "e") == 2
    assert "written by a newer tadu format; this tool will not rewrite it" in (
        capsys.readouterr().err
    )
    (root / "todo" / "closed" / f"{ID}.json").write_text("{")
    assert close(root, "--evidence", "e") == 2
    assert "not JSON" in capsys.readouterr().err


def test_other_commands_say_how_to_finish_instead_of_ambiguous(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, sample_task(1, "done"), sample_task(1))
    assert main(["set", ID, "priority=high", "--root", str(root), "--write"]) == 2
    assert capsys.readouterr().err == (
        f"tadu set: {ID}: in open/ and closed/, as a close that stopped halfway leaves it; "
        f"run tadu close --id {ID} again to finish it\n"
    )


def test_a_closed_copy_changed_meanwhile_stops_the_finish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, sample_task(1, "done"), sample_task(1))
    monkeypatch.setattr("tadu.run_task_close.backlog_unchanged", lambda *_: False)
    assert close(root, "--evidence", "CI green") == 2
    capsys.readouterr()
    assert (root / "todo" / "open" / f"{ID}.json").exists()
    assert closed(root)["evidence"] == ["pytest passes"]
