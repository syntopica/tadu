from datetime import date
from pathlib import Path

import pytest

from tadu.closing import Closing
from tadu.plan_close import plan_close

CLOSING = Closing("x", "e", None, None, None, date(2026, 10, 19))
LOG = "# Log\n\n<!-- tadu:log v1 since 2026-10-01 -->\n"


def test_emptied_backlog_keeps_its_legend(tmp_path: Path) -> None:
    plan = plan_close(tmp_path, ("- [ ] target\n", LOG), 0, CLOSING)
    assert plan is not None
    assert "States:" in plan.todo[2]
    assert plan.line == 1


def test_close_that_adds_errors_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = Closing("x", "e", None, None, "x\u2028- [x] 2026-10-19 — injected", date(2026, 10, 19))
    todo = "# TODO\n\n- [ ] a\n- [x] stray\n"
    assert plan_close(tmp_path, (todo, LOG), 2, CLOSING) is not None
    assert plan_close(tmp_path, ("# TODO\n\n- [ ] a\n", LOG), 2, bad) is None
    assert "would add doctor errors" in capsys.readouterr().err
