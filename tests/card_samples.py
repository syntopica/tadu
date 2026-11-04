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
            estimate=30,
        ),
        problems=(FieldProblem(4, "bad"),),
    )
    return Card(item, "shop", "backlog", "storefront", (("client", "acme"),), "e", "r")
