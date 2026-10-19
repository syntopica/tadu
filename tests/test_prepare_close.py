from datetime import date
from pathlib import Path

import pytest

from tadu.closing import Closing
from tadu.prepare_close import prepare_close

CLOSING = Closing("x", "e", None, None, None, date(2026, 10, 19))


def test_refusals(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert prepare_close(tmp_path, "a", CLOSING) is None
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    (tmp_path / "TODO.md").write_text("- [ ] a\n")
    assert prepare_close(tmp_path, "zzz", CLOSING) is None
    (tmp_path / "TODO.md").write_bytes(b"- [ ] a\r\n- [ ] b\n")
    assert prepare_close(tmp_path, "a", CLOSING) is None
    assert "TODO.md:1: irregular line endings" in capsys.readouterr().err


def test_plan(tmp_path: Path) -> None:
    (tmp_path / "TODO_LOG.md").write_text("# Log\n")
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] a\n")
    plan = prepare_close(tmp_path, "a", CLOSING)
    assert plan is not None
    assert "- [x] 2026-10-19 — **General:** a" in plan.log[2]
