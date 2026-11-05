from dataclasses import replace

from card_samples import sample_card

from tadu.card import Card
from tadu.stable_card_index import stable_card_index


def card(key: str, state: str, repository: str, *, stable: bool = True) -> Card:
    base = sample_card()
    item = replace(base.item, key=key, state=state, stable=stable)
    return replace(base, item=item, repository=repository)


def test_open_card_wins_over_closed() -> None:
    closed, opened = card("t-1", "x", "old"), card("t-1", "~", "new")
    assert stable_card_index((closed, opened))["t-1"] is opened


def test_first_card_kept_otherwise() -> None:
    first, second = card("t-1", " ", "a"), card("t-1", "!", "b")
    assert stable_card_index((first, second))["t-1"] is first
    done, cancelled = card("t-2", "x", "a"), card("t-2", "-", "b")
    assert stable_card_index((done, cancelled))["t-2"] is done


def test_derived_keys_left_out() -> None:
    assert stable_card_index((card("k-1", " ", "a", stable=False),)) == {}
