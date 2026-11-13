from datetime import date, datetime

import pytest

from tadu.optional_date import optional_date
from tadu.workspace_error import WorkspaceError


def test_absent_and_date() -> None:
    assert optional_date({}, "view", "due_before") is None
    day = date(2026, 12, 31)
    assert optional_date({"due_before": day}, "view", "due_before") == day


@pytest.mark.parametrize("value", ["2026-12-31", datetime(2026, 12, 31, 1, 0)])  # noqa: DTZ001
def test_anything_but_a_date_is_an_error(value: object) -> None:
    with pytest.raises(WorkspaceError, match=r"^view: due_before must be a date"):
        optional_date({"due_before": value}, "view", "due_before")
