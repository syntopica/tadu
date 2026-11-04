from datetime import date
from pathlib import Path

from tadu.read_open_items import read_open_items
from tadu.scan_items import scan_items


def test_open_items_with_fields_and_derived_keys() -> None:
    lines = [
        "# TODO",
        "",
        "- [ ] Same.",
        "",
        "- [~] Same.",
        "",
        "  ID: t-55161023-f3a9-43a3-94df-589ca752fa13",
        "",
        "- [ ] Same.",
        "  - [ ] nested step",
        "```",
        "- [ ] fenced",
        "```",
    ]
    items = scan_items(lines, "shop", "TODO.md", " ~!")
    assert [(i.line, i.end_line, i.state, i.stable) for i in items] == [
        (3, 3, " ", False),
        (5, 7, "~", True),
        (9, 10, " ", False),
    ]
    assert items[1].key == "t-55161023-f3a9-43a3-94df-589ca752fa13"
    assert items[0].key != items[2].key
    assert scan_items(lines, "shop", "TODO.md", " ~!")[0].key == items[0].key
    assert items[2].text == "- [ ] Same.\n  - [ ] nested step"


def test_closed_items_are_filtered_but_counted_and_day_parsed() -> None:
    lines = ["- [x] 2026-11-01 — Same.", "- [ ] Same.", "- [-] 2026-13-45 — Bad."]
    (item,) = scan_items(lines, "shop", "TODO.md", " ")
    both = scan_items(lines, "shop", "TODO.md", " x-")
    assert item.key == both[1].key != both[0].key
    assert both[0].day == date(2026, 11, 1)
    assert both[0].title == "Same."
    assert both[2].day is None


def test_crlf_titles_and_fields_have_no_carriage_return(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"- [ ] Fix it.\r\n\r\n  Priority: high\r\n")
    (item,) = read_open_items(tmp_path, ".", "shop")
    assert item.title == "Fix it."
    assert item.fields.priority == "high"


def test_wrapped_titles_feed_the_item_and_its_key() -> None:
    lines = ["- [ ] Fix the", "  checkout.", "- [ ] Fix the", "  checkout."]
    first, second = scan_items(lines, "shop", "TODO.md", " ")
    assert first.title == "Fix the checkout."
    assert first.key != second.key
    assert scan_items(["- [ ] Fix the checkout."], "shop", "TODO.md", " ")[0].key == first.key
