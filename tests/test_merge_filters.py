from datetime import date

from tadu.card_filter import CardFilter
from tadu.merge_filters import merge_filters


def test_flags_override_and_unset_flags_keep_the_view() -> None:
    view = CardFilter(label="bug", priority="high", include_cancelled=True)
    flags = CardFilter(priority="urgent", due_before=date(2026, 1, 1))
    assert merge_filters(view, flags) == CardFilter(
        label="bug", priority="urgent", due_before=date(2026, 1, 1), include_cancelled=True
    )


def test_include_cancelled_flag_adds_to_the_view() -> None:
    assert merge_filters(CardFilter(), CardFilter(include_cancelled=True)).include_cancelled
