import json
from datetime import date
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.check_task_backlog import check_task_backlog
from tadu.cli import main
from tadu.doctor_checks import DOCTOR_CHECKS
from tadu.doctor_checks_for import doctor_checks_for
from tadu.task_backlog_findings import task_backlog_findings

TODAY = date(2026, 11, 16)


def codes(root: Path) -> list[str]:
    return sorted(finding.code for finding in task_backlog_findings(root, TODAY))


def ident(number: int) -> str:
    return str(sample_task(number)["id"])


def test_a_clean_backlog_and_the_checks_it_gets(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [sample_task(1), sample_task(2, "done")])
    assert codes(root) == []
    assert check_task_backlog(root) == ()
    assert doctor_checks_for(root)[0] is check_task_backlog
    assert doctor_checks_for(tmp_path / "v1") == DOCTOR_CHECKS


def test_configuration_findings(tmp_path: Path) -> None:
    (tmp_path / "todo").mkdir()
    assert codes(tmp_path) == ["C001"]
    (tmp_path / "todo" / "tadu.json").write_text("{")
    assert codes(tmp_path) == ["C002"]
    (tmp_path / "todo" / "tadu.json").write_text('{"tadu": 2}')
    assert codes(tmp_path) == ["C002"]
    (tmp_path / "todo" / "tadu.json").write_bytes(b"\xff")
    assert codes(tmp_path) == ["E001"]


def test_file_findings(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [sample_task(1)])
    open_dir = root / "todo" / "open"
    (open_dir / "broken.json").write_text("{")
    (open_dir / "no-id.json").write_text(
        json.dumps({k: v for k, v in sample_task(7).items() if k != "id"})
    )
    (open_dir / "newer.json").write_text(json.dumps({**sample_task(2), "tadu": 3}))
    (open_dir / f"{ident(3)}.json").write_text(json.dumps({**sample_task(3), "state": "odd"}))
    (open_dir / f"{ident(4)}.json").write_text(json.dumps(sample_task(4)))
    (open_dir / "renamed.json").write_text(json.dumps(sample_task(5), indent=2) + "\n")
    (open_dir / f"{ident(6)}.json").write_text(
        json.dumps(sample_task(6, notes=["key: AKIA" + "Q7XJ" * 4]), indent=2) + "\n"
    )
    assert codes(root) == ["J001", "J002", "J003", "J003", "J004", "J005", "J017"]


def test_location_and_duplicate_findings(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [sample_task(1)])
    todo = root / "todo"
    (todo / "closed" / f"{ident(2)}.json").parent.mkdir()
    (todo / "closed" / f"{ident(2)}.json").write_text(json.dumps(sample_task(2), indent=2) + "\n")
    (todo / "open" / f"{ident(3)}.json").write_text(
        json.dumps(sample_task(3, "done"), indent=2) + "\n"
    )
    (todo / "closed" / f"{ident(1)}.json").write_text(json.dumps(sample_task(1), indent=2) + "\n")
    archived = todo / "archive" / "2025" / f"{ident(4)}.json"
    archived.parent.mkdir(parents=True)
    archived.write_text(json.dumps(sample_task(4, "done"), indent=2) + "\n")
    assert codes(root) == ["C003", "J006", "J006", "J006", "J006", "J007"]


def test_archive_layouts(tmp_path: Path) -> None:
    root = task_backlog(
        tmp_path, [], {"tadu": 2, "categories": {"core": "Core"}, "archive": {"after_days": 1}}
    )
    year = root / "todo" / "archive" / "2026"
    for number, folder in ((1, year), (2, year / "11")):
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{ident(number)}.json").write_text(
            json.dumps(sample_task(number, "done"), indent=2) + "\n"
        )
    assert codes(root) == ["J006"]


def test_vocabulary_findings(tmp_path: Path) -> None:
    config = {
        "tadu": 2,
        "categories": {"core": "Core"},
        "types": ["feature"],
        "stale_after_days": 5,
    }
    tasks = [
        sample_task(1, category="ui", type="bug", milestone="v9"),
        sample_task(2, priority="untriaged", category="general", type="untriaged"),
        sample_task(3, "in_progress", started="2026-11-01"),
        sample_task(4, "in_progress", started="2026-11-14"),
        sample_task(5, prority="high"),
        sample_task(6, "done", category="general", type="untriaged"),
    ]
    found = {
        (f.code, f.message)
        for f in task_backlog_findings(task_backlog(tmp_path, tasks, config), TODAY)
    }
    assert ("J008", "category 'ui' is not declared in tadu.json") in found
    assert ("J009", "type 'bug' is not declared in tadu.json") in found
    assert ("J019", "milestone 'v9' is not declared in tadu.json") in found
    assert ("J010", "needs triage: priority untriaged, category general, type untriaged") in found
    assert (
        "J018",
        "in progress for 15 days (started 2026-11-01): finish, hand over or block it",
    ) in found
    assert ("J011", "unknown key(s) prority; kept, but check for a typo") in found
    assert len(found) == 6


def test_relation_findings(tmp_path: Path) -> None:
    tasks = [
        sample_task(1, "blocked", blocked_by=[ident(2)]),
        sample_task(2, "blocked", blocked_by=[ident(1)]),
        sample_task(3, blocked_by=[ident(4)]),
        sample_task(4),
        sample_task(5, "blocked", blocked_by=[ident(6)]),
        sample_task(6, "done"),
        sample_task(7, related=[ident(99)], discovered_from=ident(7)),
        sample_task(8, "cancelled", duplicate_of=ident(9)),
        sample_task(9, "cancelled", duplicate_of=ident(4)),
        sample_task(10, "blocked", blocked_by=[ident(8), ident(11)]),
        sample_task(11, "cancelled"),
    ]
    assert codes(task_backlog(tmp_path, tasks)) == [
        *("J012", "J013", "J014", "J014", "J015", "J016", "J016", "J020", "J021"),
    ]


def test_todo_md_beside_a_task_backlog(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [])
    (root / "TODO.md").write_text("# TODO\n")
    assert codes(root) == ["C004"]


def test_doctor_command_on_a_task_backlog(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1, state="odd")])
    (root / "AGENTS.md").write_text("<!-- tadu:rule v4 -->\n<!-- /tadu:rule -->\n")
    assert main(["doctor", str(root)]) == 1
    out = capsys.readouterr().out
    assert "error J003 state must be one of pending" in out
    assert "T001" not in out
