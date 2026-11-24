import json
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main


def test_compact_list_omits_body_but_keeps_identifiers_and_filters(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1, notes=["large body " * 1000])])
    assert main(["list", str(root), "--open", "--json", "--compact"]) == 0
    compact = json.loads(capsys.readouterr().out)
    assert "text" not in compact
    assert compact["title"] == "Task 1"
    assert compact["key"] == sample_task(1)["id"]
    assert main(["list", str(root), "--open", "--json"]) == 0
    full = json.loads(capsys.readouterr().out)
    assert "large body" in full.pop("text")
    assert compact == full
