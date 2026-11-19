from tadu.backlog_item import BacklogItem
from tadu.item_similarity import item_similarity
from tadu.markdown_items import markdown_items


def item(text: str) -> BacklogItem:
    return markdown_items(text, "shop", "TODO.md")[0]


def test_closing_keeps_the_title_alike() -> None:
    old = item("- [ ] Fix login")
    new = item("- [x] 2026-11-01 — **Backend:** Fix login.\n  - Result: Fixed.")
    assert item_similarity(old, new) == 1.0


def test_kept_body_lines_outweigh_a_new_title() -> None:
    old = item("- [ ] Fix login\n\n  Cookie dropped.\n\n  On redirect only.")
    new = item("- [ ] Keep the session\n\n  Cookie dropped.\n\n  On redirect only.")
    assert item_similarity(old, new) == 1.0


def test_one_body_line_is_not_enough() -> None:
    old = item("- [ ] Fix login\n\n  Done when: tests pass.")
    new = item("- [ ] Ship export\n\n  Done when: tests pass.")
    assert item_similarity(old, new) < 0.6
