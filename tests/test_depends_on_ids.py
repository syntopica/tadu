from tadu.depends_on_ids import depends_on_ids
from tadu.fenced_lines import fenced_lines

LINES = [
    "- [ ] Ship it.",
    "",
    "  Depends on: t-55161023-f3a9-43a3-94df-589ca752fa13, the review",
    "  and t-0b5e4f1c-2a3d-4e5f-8a9b-0c1d2e3f4a5b too.",
    "",
    "  Depends on: t-55161023-f3a9-43a3-94df-589ca752fa13 again",
    "",
    "  Note: unrelated",
    "  Depends on: t-55161023-f3a9-43a3-94df-589ca752fa14 follows text",
    "",
    "  ```",
    "  Depends on: t-55161023-f3a9-43a3-94df-589ca752fa15",
    "  ```",
    "",
    "  Depends on: the design review",
]


def test_ids_from_unfenced_paragraphs_in_order_without_repeats() -> None:
    assert depends_on_ids(LINES, fenced_lines(LINES), 0, len(LINES)) == (
        "t-55161023-f3a9-43a3-94df-589ca752fa13",
        "t-0b5e4f1c-2a3d-4e5f-8a9b-0c1d2e3f4a5b",
    )


def test_end_bounds_the_paragraph() -> None:
    assert depends_on_ids(LINES, fenced_lines(LINES), 0, 3) == (
        "t-55161023-f3a9-43a3-94df-589ca752fa13",
    )


def test_item_without_dependencies() -> None:
    lines = ["- [ ] Alone.", "", "  Done when: tests pass."]
    assert depends_on_ids(lines, fenced_lines(lines), 0, len(lines)) == ()
