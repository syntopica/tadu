from datetime import date
from pathlib import Path

from sample_task import sample_task
from task_backlog import task_backlog

from tadu.task_backlog_findings import task_backlog_findings

TODAY = date(2026, 11, 16)


def contradictions(tmp_path: Path, *tasks: dict[str, object]) -> list[str]:
    findings = task_backlog_findings(task_backlog(tmp_path, list(tasks)), TODAY)
    return [f.message for f in findings if f.code == "J023"]


def test_each_format_1_contradiction_is_found_on_the_keys_of_a_task(tmp_path: Path) -> None:
    late = {"due": "2026-11-20", "defer_until": "2026-11-25", "check_on": "2026-11-30"}
    assert contradictions(
        tmp_path,
        sample_task(1, **late),
        sample_task(2, "in_progress", defer_until="2026-12-01", kind="later", started="2026-11-01"),
        sample_task(3, queue="ready", kind="waiting"),
    ) == [
        "defer_until 2026-11-25 is after due 2026-11-20",
        "check_on 2026-11-30 is after due 2026-11-20",
        "the task is in progress but defer_until 2026-12-01 is ahead",
        "kind later contradicts a task in progress",
        "queue ready contradicts kind waiting",
    ]


def test_consistent_and_closed_tasks_say_nothing(tmp_path: Path) -> None:
    fine = {"due": "2026-11-30", "defer_until": "2026-11-20", "check_on": "2026-11-25"}
    closed = sample_task(2, "done", due="2026-11-01", check_on="2026-12-01")
    assert contradictions(tmp_path, sample_task(1, **fine), closed) == []
