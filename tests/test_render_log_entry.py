from datetime import date

from tadu.closing import Closing
from tadu.render_log_entry import render_log_entry

DAY = date(2026, 10, 19)


def closing(**overrides: str | None) -> Closing:
    fields: dict[str, str | None] = {"result": None, "category": None, "title": None}
    fields.update(overrides)
    return Closing("x", "pytest green", fields["result"], fields["category"], fields["title"], DAY)


def test_section_becomes_the_category_and_continuation_is_kept() -> None:
    lines = render_log_entry(["- [ ] Fix it", "  - acceptance: ok"], closing(result="done"), "UI")
    assert lines == [
        "- [x] 2026-10-19 — **UI:** Fix it",
        "  - acceptance: ok",
        "  - Result: done",
        "  - Evidence: pytest green",
    ]


def test_existing_category_prefix_is_kept() -> None:
    lines = render_log_entry(["- [~] **Bugs:** crash"], closing(), "UI")
    assert lines[0] == "- [x] 2026-10-19 — **Bugs:** crash"


def test_explicit_category_replaces_the_prefix_and_title_the_text() -> None:
    lines = render_log_entry(["- [!] **Bugs:** crash"], closing(category="Ops"), None)
    assert lines[0] == "- [x] 2026-10-19 — **Ops:** crash"
    lines = render_log_entry(["- [ ] a"], closing(title="Better title"), None)
    assert lines[0] == "- [x] 2026-10-19 — **General:** Better title"


def test_resolution_for_an_obsolete_item() -> None:
    dropped = Closing("-", "superseded", None, None, None, DAY)
    assert render_log_entry(["- [ ] a"], dropped, None)[-1] == "  - Resolution: superseded"
