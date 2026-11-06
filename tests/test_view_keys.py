from tadu.card_filter import CardFilter
from tadu.view_keys import VIEW_KEYS


def test_name_plus_every_filter_field() -> None:
    assert frozenset({"name", *CardFilter.__dataclass_fields__}) == VIEW_KEYS
