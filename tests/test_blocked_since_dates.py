from dataclasses import replace
from pathlib import Path

import pytest
from card_samples import sample_card
from git_checkout import commit_file

from tadu.blocked_since_dates import blocked_since_dates
from tadu.local_date import local_date

OLD, NEW = 1_700_000_000, 1_750_000_000


def test_dates_blocked_items_from_their_first_line(tmp_path: Path) -> None:
    commit_file(tmp_path, "TODO.md", "# TODO\n- [!] a\n- [!] b\n", OLD)
    commit_file(tmp_path, "TODO.md", "# TODO\n- [!] a\n- [!] b2\n- [ ] c\n", NEW)
    base = replace(sample_card().item, state="!")
    items = (replace(base, line=2), replace(base, line=3), replace(base, line=4, state=" "))
    assert blocked_since_dates(items, tmp_path) == (local_date(OLD), local_date(NEW), None)


def test_blames_each_file_once(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[str] = []

    def fake(_: Path, path: str) -> None:
        calls.append(path)

    monkeypatch.setattr("tadu.blocked_since_dates.git_blame_output", fake)
    item = replace(sample_card().item, state="!")
    assert blocked_since_dates((item, item), tmp_path) == (None, None)
    assert calls == ["TODO.md"]
