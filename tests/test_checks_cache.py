import json
from datetime import date
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

import tadu.cached_payloads
import tadu.checked_task_files
from tadu.task_backlog_findings import task_backlog_findings

TODAY = date(2026, 11, 16)


@pytest.fixture(autouse=True)
def trusting(monkeypatch: pytest.MonkeyPatch) -> None:
    """Treat files written a moment ago as old enough to cache."""
    monkeypatch.setattr(tadu.cached_payloads, "RACY_NANOSECONDS", -(10**12))


def backlog(tmp_path: Path) -> Path:
    root = task_backlog(tmp_path, [sample_task(1), sample_task(2, "done", closed="2026-11-10")])
    (root / "todo" / "open" / "t-bad.json").write_text("{")
    (root / "todo" / "open" / f"{sample_task(3)['id']}.json").write_text(
        json.dumps(sample_task(3, notes=["key: AKIA" + "Q7XJ" * 4]))
    )
    return root


def codes(root: Path) -> list[str]:
    return sorted(f.code for f in task_backlog_findings(root, TODAY))


def test_second_run_reads_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = backlog(tmp_path)
    first = codes(root)
    assert first == ["J001", "J004", "J017"]
    monkeypatch.setattr(tadu.checked_task_files, "checked_payload", None)
    assert codes(root) == first


def test_malformed_cached_checks_are_recomputed(tmp_path: Path, private_item_cache: Path) -> None:
    root = backlog(tmp_path)
    first = codes(root)
    for cache in private_item_cache.glob("checks-*"):
        data = json.loads(cache.read_text())
        for number, entry in enumerate(data["entries"].values()):
            entry[1] = [["short"], [None, None, False, [], None], [1, 2, 3, 4, 5]][number % 3]
        cache.write_text(json.dumps(data))
    assert codes(root) == first
