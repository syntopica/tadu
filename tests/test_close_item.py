from datetime import date

from tadu.close_item import close_item
from tadu.closing import Closing

CLOSING = Closing("x", "e", None, None, None, date(2026, 10, 19))


def test_item_moves_from_the_backlog_into_the_log() -> None:
    todo = ["# TODO", "", "## UI", "", "- [ ] a", "  more", "", "- [ ] b", ""]
    log = ["# Log", "", "<!-- tadu:log v1 since 2026-10-01 -->", ""]
    new_todo, new_log = close_item(todo, log, 4, CLOSING)
    assert new_todo == ["# TODO", "", "## UI", "", "- [ ] b", ""]
    assert new_log[4:] == [
        "## 2026",
        "",
        "### 2026-10",
        "",
        "- [x] 2026-10-19 — **UI:** a",
        "  more",
        "  - Evidence: e",
        "",
    ]
