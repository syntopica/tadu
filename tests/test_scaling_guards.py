"""Work that grows with what is asked, not with the size of the backlog.

Counted, not timed, so they hold on any machine: each guards a fix measured on a backlog
of 27,500 tasks (bench/format-study/bench_tadu.py, scale L).
"""

import re
from datetime import date
from pathlib import Path

import pytest

from tadu.backlog_item import BacklogItem
from tadu.build_backlog_item import build_backlog_item
from tadu.cli import main
from tadu.read_recent_log_items import read_recent_log_items

OLD = "".join(
    f"- [x] 2025-01-{n % 28 + 1:02d} — Old task {n}.\n\n  Evidence: ok\n\n" for n in range(2_000)
)
RECENT = "".join(
    f"- [x] 2026-11-{n + 10:02d} — Recent task {n}.\n\n  Evidence: ok\n\n" for n in range(5)
)


def test_the_done_window_builds_only_the_entries_in_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "TODO_LOG.md").write_text(
        "# Log\n\n<!-- tadu:log v1 since 2024-01-01 -->\n\n" + RECENT + OLD
    )
    built: list[BacklogItem] = []

    def counted(
        lines: list[str], fenced: list[bool], match: re.Match[str], at: tuple[int, str, str, str]
    ) -> BacklogItem:
        built.append(build_backlog_item(lines, fenced, match, at))
        return built[-1]

    monkeypatch.setattr("tadu.scan_items.build_backlog_item", counted)
    items = read_recent_log_items(tmp_path, ".", "shop", date(2026, 11, 2))
    assert [item.title for item in items] == [f"Recent task {n}." for n in range(5)]
    assert len(built) == 5


def test_closing_one_item_of_a_long_log_prints_a_short_diff(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "TODO.md").write_text(
        "# TODO\n\nStates: [ ] open, [~] in progress, [!] blocked.\n\n- [ ] Ship the thing.\n"
    )
    (tmp_path / "TODO_LOG.md").write_text(
        "# Log\n\n<!-- tadu:log v1 since 2024-01-01 -->\n\n## 2025\n\n### 2025-01\n\n" + OLD
    )
    monkeypatch.chdir(tmp_path)
    main(["close", "--match", "Ship the thing", "--evidence", "CI green", "--write"])
    printed = capsys.readouterr().out
    assert "Ship the thing" in printed
    assert len(printed.splitlines()) < 40
