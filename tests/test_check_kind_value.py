import pytest

from tadu.check_kind_value import check_kind_value


@pytest.mark.parametrize("value", ["task", "decision", "waiting", "later"])
def test_known(value: str) -> None:
    assert check_kind_value(value) is None


@pytest.mark.parametrize("value", ["someday", "Decision", "", "waiting on ana"])
def test_unknown(value: str) -> None:
    assert check_kind_value(value) == "Kind is not one of task, decision, waiting, later"
