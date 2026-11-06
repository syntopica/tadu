from datetime import date, datetime

import pytest

from tadu.optional_date import optional_date
from tadu.workspace_error import WorkspaceError


def test_absent_and_date() -> None:
    assert optional_date({}, "view", "due") is None
    assert optional_date({"due": date(2026, 1, 2)}, "view", "due") == date(2026, 1, 2)


@pytest.mark.parametrize("value", ["2026-01-02", datetime(2026, 1, 2, 3, 4), 5])  # noqa: DTZ001
def test_rejects_non_dates(value: object) -> None:
    with pytest.raises(WorkspaceError, match=r"^view: due must be a date"):
        optional_date({"due": value}, "view", "due")
