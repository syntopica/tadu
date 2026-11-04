import json
from pathlib import Path

import pytest

from tadu.cli import main
from tadu.run_id import run_id

TODO = "# TODO\n\n## UI\n\n- [ ] fix header\n- [ ] other\n"


def keys(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> list[str]:
    capsys.readouterr()
    assert main(["list", str(tmp_path), "--json"]) == 0
    return [json.loads(line)["key"] for line in capsys.readouterr().out.splitlines()]


def test_dry_run_prints_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text(TODO)
    assert run_id(str(tmp_path), None, write=False) == 0
    assert "+  ID: t-" in capsys.readouterr().out
    assert (tmp_path / "TODO.md").read_text() == TODO


def test_write_by_key_gives_one_item_a_stable_key(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text(TODO)
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    first, second = keys(tmp_path, capsys)
    assert run_id(str(tmp_path), second, write=True) in (0, 1)
    now = keys(tmp_path, capsys)
    assert now[0] == first
    assert now[1].startswith("t-")
    assert run_id(str(tmp_path), None, write=True) in (0, 1)
    assert all(key.startswith("t-") for key in keys(tmp_path, capsys))


def test_nothing_to_do_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    assert run_id(str(tmp_path), None, write=True) == 0
    assert (tmp_path / "TODO.md").read_text() == "# TODO\n"
    capsys.readouterr()


def test_refusals_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_id(str(tmp_path / "absent"), None, write=False) == 2
    assert "not a directory" in capsys.readouterr().err
    assert run_id(str(tmp_path), None, write=True) == 2
    capsys.readouterr()


def test_failed_write_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "TODO.md").write_text(TODO)
    monkeypatch.setattr("tadu.run_id.write_backlog_file", lambda *_args: False)
    assert run_id(str(tmp_path), None, write=True) == 2
    capsys.readouterr()
