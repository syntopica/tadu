import json
from pathlib import Path

import pytest
from local_today import local_today
from sample_task import sample_id, sample_task
from task_backlog import task_backlog

from tadu.cli import main

TODAY = local_today().isoformat()


def task_at(root: Path, number: int) -> dict[str, object]:
    path = next((root / "todo").rglob(f"{sample_id(number)}.json"))
    data: dict[str, object] = json.loads(path.read_text())
    return data


def test_add_shows_similar_tasks_then_writes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = task_backlog(tmp_path, [sample_task(1, title="Fix the race condition in autocomplete")])
    args = [
        "add",
        str(root),
        "--title",
        "Resolve the race condition in autocomplete",
        "--category",
        "core",
    ]
    assert main(args) == 0
    captured = capsys.readouterr().out.splitlines()
    assert captured[0].startswith("similar 0.75: ")
    assert captured[1].endswith("(dry run: add --write)")
    assert not list((root / "todo" / "open").glob("t-*.json"))[1:]
    monkeypatch.setenv("TADU_ACTOR", "agent:claude")
    extra = [
        "--type",
        "bug",
        "--priority",
        "high",
        "--label",
        "search",
        "--note",
        "Seen twice.",
        "--blocked-by",
        "t-00000001",
    ]
    assert main([*args, *extra, "--discovered-from", sample_id(1), "--write"]) == 0
    written = [
        json.loads(p.read_text())
        for p in (root / "todo" / "open").glob("*.json")
        if sample_id(1) not in p.name
    ]
    assert len(written) == 1
    task = written[0]
    assert (task["state"], task["created"], task["created_by"]) == (
        "blocked",
        TODAY,
        "agent:claude",
    )
    assert task["blocked_by"] == [sample_id(1)]
    assert task["discovered_from"] == sample_id(1)
    assert task["notes"] == ["Seen twice."]


def test_add_refusals(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["add", str(tmp_path), "--title", "x"]) == 2
    assert "TODO.md: missing; start the backlog with `tadu init`" in capsys.readouterr().err
    root = task_backlog(tmp_path, [])
    assert main(["add", str(root), "--title", "x", "--due", "soon"]) == 2
    assert (
        "refused, the task would be invalid: due must be a YYYY-MM-DD date"
        in capsys.readouterr().err
    )
    assert main(["add", str(root), "--title", "x", "--related", "t-12345678"]) == 2
    assert "t-12345678: no such task" in capsys.readouterr().err


def test_set(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = task_backlog(tmp_path, [sample_task(1, labels=["a"]), sample_task(2)])
    base = ["set", "t-00000001", "--root", str(root)]
    assert (
        main([*base, "priority=urgent", "labels+=b,a", "notes+=One.", "notes+=Two.", "estimate=30"])
        == 0
    )
    assert "labels, notes, priority" in capsys.readouterr().out
    assert task_at(root, 1)["priority"] == "normal"
    assert (
        main([*base, "priority=urgent", "labels+=b,a", "notes+=One.", "estimate=30", "--write"])
        == 0
    )
    capsys.readouterr()
    task = task_at(root, 1)
    assert (task["priority"], task["labels"], task["notes"], task["estimate"]) == (
        "urgent",
        ["a", "b"],
        ["One."],
        30,
    )
    assert (
        main(
            [
                *base,
                "labels-=a",
                "related=t-00000002",
                "parent=t-00000002",
                "state=in_progress",
                "--write",
            ]
        )
        == 0
    )
    task = task_at(root, 1)
    assert (task["labels"], task["related"], task["parent"]) == (
        ["b"],
        [sample_id(2)],
        sample_id(2),
    )
    assert (task["state"], task["started"]) == ("in_progress", TODAY)
    assert main([*base, "estimate=\u00b2", "--write"]) == 2
    assert main([*base, "x-jira=T-1", "estimate=", "--write"]) == 0
    assert "estimate" not in task_at(root, 1)
    assert task_at(root, 1)["x-jira"] == "T-1"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ("priority", "write key=value, key+=value, key-=value or key="),
        ("started=2026-01-01", "started: set by tadu itself"),
        ("colour=red", "colour: not a task key"),
        ("state=done", "state: use tadu close to close a task"),
        ("priority+=high", "priority is not a list: use priority=value"),
        (
            "state=blocked",
            "refused, the task would be invalid: a blocked task needs blocker or blocked_by",
        ),
    ],
)
def test_set_refusals(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], change: str, message: str
) -> None:
    root = task_backlog(tmp_path, [sample_task(1)])
    assert main(["set", "t-00000001", change, "--root", str(root), "--write"]) == 2
    assert message in capsys.readouterr().err
    assert task_at(root, 1) == sample_task(1)


def test_set_refuses_an_ambiguous_prefix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    twins = [sample_task(n, id=f"t-abcdef12-0000-4000-8000-00000000000{n}") for n in (1, 2)]
    root = task_backlog(tmp_path, twins)
    assert main(["set", "t-abcdef12", "priority=high", "--root", str(root)]) == 2
    assert (
        "t-abcdef12: ambiguous: t-abcdef12-0000-4000-8000-000000000001, t-abcdef12"
        in capsys.readouterr().err
    )


def test_claim_a_task_whose_blocker_is_closed(tmp_path: Path) -> None:
    root = task_backlog(
        tmp_path, [sample_task(1, "done"), sample_task(2, blocked_by=[sample_id(1)])]
    )
    assert main(["claim", sample_id(2), "--as", "ana", "--root", str(root), "--write"]) == 0
    assert task_at(root, 2)["state"] == "in_progress"


def test_set_never_rewrites_a_newer_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [])
    path = root / "todo" / "open" / f"{sample_id(1)}.json"
    path.parent.mkdir()
    path.write_text(json.dumps({**sample_task(1), "tadu": 3}))
    assert main(["set", sample_id(1), "priority=high", "--root", str(root), "--write"]) == 2
    assert "written by a newer tadu format" in capsys.readouterr().err


def test_claim(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    tasks = [
        sample_task(1),
        sample_task(2, "blocked", blocker="Vendor."),
        sample_task(3, "in_progress", assignees=["bob"], started="2026-11-10"),
        sample_task(4, defer_until="2999-01-01"),
        sample_task(5, "done"),
        sample_task(6, blocked_by=[sample_id(1)]),
        sample_task(7, blocked_by=["t-0000dead-0000-4000-8000-000000000000"]),
    ]
    root = str(task_backlog(tmp_path, tasks))
    assert main(["claim", "t-00000001", "--as", "agent:claude", "--root", root, "--write"]) == 0
    task = task_at(Path(root), 1)
    assert (task["state"], task["assignees"], task["started"]) == (
        "in_progress",
        ["agent:claude"],
        TODAY,
    )
    for number, reason in (
        (2, "it is blocked: Vendor."),
        (3, "it is in progress by bob (use --force to take it over)"),
        (4, "it is deferred until 2999-01-01"),
        (5, "it is done"),
        (6, f"it is blocked: {sample_id(1)}"),
        (7, "it is blocked: t-0000dead"),
    ):
        assert main(["claim", sample_id(number), "--as", "ana", "--root", root]) == 2
        assert reason in capsys.readouterr().err
    assert main(["claim", sample_id(2), "--as", "ana", "--force", "--root", root]) == 2
    assert main(["claim", sample_id(3), "--as", "ana", "--force", "--root", root, "--write"]) == 0
    assert "claimed" in capsys.readouterr().out
    assert (task_at(Path(root), 3)["assignees"], task_at(Path(root), 3)["started"]) == (
        ["ana"],
        "2026-11-10",
    )
    assert main(["claim", sample_id(1), "--as", "bob", "--root", root]) == 2
    assert main(["claim", "t-1", "--as", "bob", "--root", root]) == 2
    assert "give a task id, or at least its first 10 characters" in capsys.readouterr().err
