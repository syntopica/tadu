from tadu.card_filter import CardFilter
from tadu.view_entry import ViewEntry


def test_holds_name_and_filter() -> None:
    entry = ViewEntry("mine", CardFilter(assignee="ana"))
    assert entry.card_filter.assignee == "ana"
