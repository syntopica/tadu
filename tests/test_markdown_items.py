from tadu.markdown_items import markdown_items


def test_open_and_closed_items() -> None:
    text = "- [ ] A.\n- [x] 2026-11-01 — B.\n- [-] C."
    items = markdown_items(text, "shop", "TODO.md")
    assert [(item.state, item.title, item.path) for item in items] == [
        (" ", "A.", "TODO.md"),
        ("x", "B.", "TODO.md"),
        ("-", "C.", "TODO.md"),
    ]


def test_empty_text() -> None:
    assert markdown_items("", "shop", "TODO.md") == ()
