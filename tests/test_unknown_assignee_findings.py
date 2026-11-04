from dataclasses import replace
from datetime import date
from pathlib import Path

from card_samples import sample_card

from tadu.card import Card
from tadu.item_fields import ItemFields
from tadu.local_config import LocalConfig
from tadu.person_entry import PersonEntry
from tadu.unknown_assignee_findings import unknown_assignee_findings
from tadu.workspace import Workspace


def card_in(column: str, state: str) -> Card:
    base = sample_card()
    item = replace(
        base.item, state=state, day=date(2026, 11, 1), fields=ItemFields(assignees=("bob",))
    )
    return Card(item, "shop", column, None, (), None, None)


def findings_for(*cards: Card) -> tuple[str, ...]:
    workspace = Workspace(Path("/w"), (), (), (), (PersonEntry("ana", "Ana", None),))
    local = LocalConfig({"shop": Path("/w/shop")}, None, None)
    return tuple(f.message for f in unknown_assignee_findings(workspace, local, cards))


def test_open_item_with_unknown_assignee_warns() -> None:
    assert findings_for(card_in("backlog", " ")) == (
        "assignee bob is not a person in the workspace",
    )


def test_closed_entries_do_not_warn() -> None:
    assert findings_for(card_in("done", "x"), card_in("cancelled", "-")) == ()
