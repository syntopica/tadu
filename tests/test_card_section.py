import pytest
from card_samples import make_card

from tadu.card_section import card_section


@pytest.mark.parametrize(
    ("state", "kind", "section"),
    [
        (" ", "task", "do"),
        ("~", "task", "do"),
        ("!", "task", "blocked"),
        (" ", "decision", "decide"),
        ("!", "decision", "decide"),
        (" ", "waiting", "chase"),
        ("!", "later", "check"),
    ],
)
def test_section_follows_kind_then_state(state: str, kind: str, section: str) -> None:
    assert card_section(make_card("x", state, kind=kind)) == section
