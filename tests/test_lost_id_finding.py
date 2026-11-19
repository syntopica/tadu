from datetime import date
from pathlib import Path

from sample_task import sample_task
from task_backlog import task_backlog

from tadu.task_backlog_findings import task_backlog_findings

LOST = str(sample_task(9)["id"])


def test_a_note_holding_another_id_is_what_an_older_migrate_lost(tmp_path: Path) -> None:
    notes = ["Context.", "", f"ID: {LOST}", f"ID: {sample_task(1)['id']}", f"See ID: {LOST}"]
    root = task_backlog(tmp_path, [sample_task(1, "done", notes=notes)])
    findings = task_backlog_findings(root, date(2026, 11, 18))
    assert [(f.code, f.severity, f.message) for f in findings] == [
        (
            "J022",
            "warning",
            (
                f"notes hold `ID: {LOST}`, an ID that an older tadu's migrate lost; "
                "tadu migrate --recover gives it back"
            ),
        )
    ]
