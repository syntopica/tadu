import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main

TODAY = datetime.now(UTC).astimezone().date().isoformat()


def ident(number: int) -> str:
    return str(sample_task(number)["id"])


def read(root: Path, folder: str, number: int) -> dict[str, object]:
    data: dict[str, object] = json.loads(
        (root / "todo" / folder / f"{ident(number)}.json").read_text()
    )
    return data


def backlog(tmp_path: Path) -> Path:
    tasks = [
        sample_task(1, title="Ship the exporter"),
        sample_task(2, "blocked", blocked_by=[ident(1)]),
        sample_task(3, "blocked", blocked_by=[ident(1), ident(4)]),
        sample_task(4, title="Ship the importer"),
        sample_task(5, "blocked", blocked_by=[ident(1)], blocker="Vendor sandbox."),
        sample_task(6, blocked_by=[ident(1)]),
    ]
    return task_backlog(tmp_path, tasks)


def test_close_as_done_reports_waiting_tasks_and_changes_none(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = backlog(tmp_path)
    before = {n: read(root, "open", n) for n in (2, 3, 5, 6)}
    assert main(["close", str(root), "--id", "t-00000001", "--evidence", "pytest passes"]) == 0
    assert read(root, "open", 1)["state"] == "pending"
    assert (
        main(["close", str(root), "--id", "t-00000001", "--evidence", "pytest passes", "--write"])
        == 0
    )
    lines = capsys.readouterr().out.splitlines()
    assert lines[-5].startswith(f"tadu close: closed {ident(1)} as done -> todo/closed/")
    assert lines[-4].endswith("nothing blocks it now; decide whether it moves to pending")
    assert lines[-3].endswith(f"still waits on {ident(4)}")
    assert lines[-2].endswith(
        "no task blocks it any more, but it is still blocked by: Vendor sandbox."
    )
    assert lines[-1].endswith("nothing blocks it now; decide whether it moves to pending")
    closed = read(root, "closed", 1)
    assert (closed["state"], closed["closed"], closed["result"]) == (
        "done",
        TODAY,
        "Ship the exporter",
    )
    assert closed["evidence"] == ["pytest passes"]
    assert not (root / "todo" / "open" / f"{ident(1)}.json").exists()
    assert {n: read(root, "open", n) for n in (2, 3, 5, 6)} == before


def test_close_by_match_as_cancelled_or_duplicate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = backlog(tmp_path)
    args = [
        "close",
        str(root),
        "--match",
        "importer",
        "--resolution",
        "Not needed.",
        "--date",
        "2026-11-02",
    ]
    assert main([*args, "--write"]) == 0
    assert "waited on this task, which is cancelled, not done: review it" in capsys.readouterr().out
    assert (read(root, "closed", 4)["state"], read(root, "closed", 4)["closed"]) == (
        "cancelled",
        "2026-11-02",
    )
    assert (
        main(["close", str(root), "--id", ident(1), "--duplicate-of", "t-00000004", "--write"]) == 0
    )
    assert f"(block on {ident(4)} instead?)" in capsys.readouterr().out
    duplicate = read(root, "closed", 1)
    assert (duplicate["duplicate_of"], duplicate["resolution"]) == (
        ident(4),
        f"Duplicate of {ident(4)}.",
    )


def test_close_refusals(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = backlog(tmp_path)
    assert main(["close", str(root), "--match", "Ship", "--evidence", "e"]) == 2
    assert "2 open tasks match 'Ship': " in capsys.readouterr().err
    assert main(["close", str(root), "--match", "nothing", "--evidence", "e"]) == 2
    assert "0 open tasks match 'nothing'\n" in capsys.readouterr().err
    assert main(["close", str(root), "--evidence", "e"]) == 2
    assert "give --id, or --match" in capsys.readouterr().err
    assert main(["close", str(root), "--id", ident(1), "--evidence", "two\nlines", "--write"]) == 2
    assert "evidence must be a list of strings without line breaks" in capsys.readouterr().err
    main(["close", str(root), "--id", ident(1), "--evidence", "e", "--write"])
    capsys.readouterr()
    assert main(["close", str(root), "--id", ident(1), "--evidence", "e"]) == 2
    assert "is already done" in capsys.readouterr().err


def test_a_v1_backlog_rejects_the_v2_options(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] fix\n")
    for extra in (["--id", "t-00000001"], ["--match", "fix", "--id", "t-1"]):
        assert main(["close", str(tmp_path), *extra, "--evidence", "e"]) == 2
        assert "needs --match, and takes no --id or --duplicate-of" in capsys.readouterr().err
    assert main(["close", str(tmp_path), "--match", "fix", "--duplicate-of", "t-1"]) == 2
