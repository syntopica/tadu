import json
from pathlib import Path

import pytest

from tadu.cli import main

ALL = ["--done-days", "99999"]


def repo(tmp_path: Path, name: str, log: str) -> Path:
    root = tmp_path / name
    root.mkdir()
    (root / "TODO.md").write_text("- [ ] Open.\n")
    (root / "TODO_LOG.md").write_text(log)
    return root


def entry(day: str, title: str, state: str = "x") -> str:
    label = "Evidence" if state == "x" else "Resolution"
    return f"## {day[:4]}\n\n### {day[:7]}\n\n- [{state}] {day} — **C:** {title}\n  - {label}: e\n"


def feed(capsys: pytest.CaptureFixture[str], *argv: str) -> list[dict[str, object]]:
    assert main(["feed", *argv]) == 0
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


def test_closed_entries_across_repositories_newest_first(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    one = repo(tmp_path, "one", entry("2020-01-02", "Old."))
    two = repo(tmp_path, "two", entry("2020-03-04", "New.", "-"))
    rows = feed(capsys, str(one), str(two), *ALL)
    assert [(r["repository"], r["title"], r["column"]) for r in rows] == [
        ("two", "**C:** New.", "cancelled"),
        ("one", "**C:** Old.", "done"),
    ]


def test_done_days_window(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert feed(capsys, str(repo(tmp_path, "one", entry("2020-01-02", "Old.")))) == []


def test_workspace_scope(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    shop = repo(tmp_path, "shop", entry("2020-01-02", "Did."))
    (tmp_path / "tadu-workspace.toml").write_text('version = 1\n[[repository]]\nkey = "shop"\n')
    (tmp_path / "tadu-workspace.local.toml").write_text(f'version = 1\n[paths]\nshop = "{shop}"\n')
    rows = feed(capsys, "--workspace", str(tmp_path), *ALL)
    assert [r["repository"] for r in rows] == ["shop"]


def test_problems_to_stderr_exit_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["feed", str(tmp_path / "gone")]) == 0
    assert capsys.readouterr().err.startswith("tadu feed: gone: ")


def test_bad_scope_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["feed", "x", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err == "tadu feed: give repository paths or --workspace, not both\n"
