from tadu.body_lines import body_lines
from tadu.markdown_items import markdown_items

TEXT = """- [x] 2026-11-01 — Fix the
  login.

  Why it broke.

  Priority: high
  - Result: Fixed."""


def test_leaves_out_title_fields_and_blank_lines() -> None:
    (item,) = markdown_items(TEXT, "shop", "TODO_LOG.md")
    assert body_lines(item) == ["  Why it broke.", "  - Result: Fixed."]
