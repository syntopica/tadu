from datetime import date

from tadu.backlog_item import BacklogItem
from tadu.card import Card
from tadu.field_problem import FieldProblem
from tadu.item_fields import ItemFields


def sample_card() -> Card:
    item = BacklogItem(
        key="k",
        stable=True,
        path="TODO.md",
        line=2,
        end_line=3,
        state=" ",
        day=date(2026, 11, 1),
        title="T",
        text="<b>T</b>",
        fields=ItemFields(
            id="t-1",
            priority="high",
            assignees=("ana",),
            due=date(2026, 12, 1),
            labels=("x",),
            queue="ready",
            kind="decision",
            estimate=30,
        ),
        problems=(FieldProblem(4, "bad"),),
    )
    return Card(item, "shop", "backlog", "storefront", (("client", "acme"),), "e", "r")


def make_card(title: str, state: str = " ", column: str = "backlog", **fields: object) -> Card:
    """An open card of shop with only the given fields set."""
    item = BacklogItem(
        key=title,
        stable=False,
        path="TODO.md",
        line=1,
        end_line=1,
        state=state,
        day=None,
        title=title,
        text=title,
        fields=ItemFields(**fields),  # type: ignore[arg-type]
        problems=(),
    )
    return Card(item, "shop", column, None, (), None, None)
