import argparse
from datetime import date
from pathlib import Path

import pytest

from tadu.close_command import close_command


def args(path: Path, **overrides: str | date | bool | None) -> argparse.Namespace:
    values: dict[str, str | date | bool | None] = {
        "path": str(path),
        "match": "fix",
        "id": None,
        "evidence": "e",
        "resolution": None,
        "result": None,
        "category": None,
        "title": None,
        "date": date(2026, 10, 19),
        "write": False,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_invalid_request_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert close_command(args(tmp_path, match=" ")) == 2
    assert "tadu close: arguments must not be blank" in capsys.readouterr().err


def test_resolution_runs_as_obsolete(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] fix\n")
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    assert close_command(args(tmp_path, evidence=None, resolution="gone", date=None)) == 0
    assert "+- [-] " in capsys.readouterr().out


def test_close_by_id(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("- [ ] fix\n\n  ID: t-1\n- [ ] fix too\n")
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    assert close_command(args(tmp_path, match=None, id="t-1")) == 0
    out = capsys.readouterr().out
    assert "+- [x] 2026-10-19 — **General:** fix\n" in out
    assert "+  ID: t-1\n" in out
    assert close_command(args(tmp_path, match=None, id="t-2")) == 2
    assert "0 open items have ID 't-2'" in capsys.readouterr().err
