from pathlib import Path

import pytest

from tadu.plan_ids import plan_ids
from tadu.task_id_pattern import TASK_ID_PATTERN


def test_plans_an_id_for_each_item_without_one(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"# TODO\r\n\r\n- [ ] a\r\n")
    plan = plan_ids(tmp_path, None)
    assert plan is not None
    target, before, after = plan
    assert (target, before) == (tmp_path / "TODO.md", "# TODO\r\n\r\n- [ ] a\r\n")
    lines = after.split("\r\n")
    assert lines[:4] == ["# TODO", "", "- [ ] a", ""]
    assert TASK_ID_PATTERN.match(lines[4].removeprefix("  ID: "))
    assert lines[5:] == [""]
    assert (tmp_path / "TODO.md").read_bytes() == b"# TODO\r\n\r\n- [ ] a\r\n"


def test_missing_backlog(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert plan_ids(tmp_path, None) is None
    assert "missing" in capsys.readouterr().err


def test_unknown_key(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] a\n")
    assert plan_ids(tmp_path, "k-0") is None
    assert "no open item has key k-0" in capsys.readouterr().err


def test_refused_item(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] a\nlazy\n")
    assert plan_ids(tmp_path, None) is None
    assert "TODO.md:1: the item has a possible unindented" in capsys.readouterr().err
