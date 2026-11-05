from dataclasses import replace

from card_samples import sample_card

from tadu.card import Card
from tadu.dependency import Dependency
from tadu.resolve_dependencies import resolve_dependencies


def card(key: str, state: str, repository: str, depends_on: tuple[str, ...] = ()) -> Card:
    base = sample_card()
    item = replace(base.item, key=key, state=state, depends_on=depends_on)
    return replace(base, item=item, repository=repository, column="backlog")


def test_targets_resolved_across_repositories() -> None:
    target = card("t-1", "!", "api")
    waiting = card("t-2", " ", "shop", ("t-1", "t-9"))
    cards = resolve_dependencies((waiting, target))
    assert cards[0].dependencies == (
        Dependency("t-1", "api", "!", "backlog"),
        Dependency("t-9", None, None, None),
    )
    assert cards[1].dependencies == ()
    assert cards[0].item is waiting.item
