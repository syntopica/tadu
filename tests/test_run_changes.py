import json
from pathlib import Path

import pytest
from changes_repo import ID, changes_repo

from tadu.cli import main

DAYS = ["--since", "2026-11-01", "--until", "2026-11-30"]


def test_text_grouped_for_a_retro(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = changes_repo(tmp_path / "shop")
    assert main(["changes", str(root), *DAYS]) == 0
    out = capsys.readouterr().out
    assert out.startswith(
        "tadu changes: 2026-11-01 to 2026-11-30 · 9 changes\n\nClosed (1) · Ana 1\n"
    )
    assert (
        "Reopened (1) · Bob 1\n  2026-11-06  Bob  shop:t-3f2a1b4c  Ship the export.  (state: done → pending)\n"
        in out
    )
    assert (
        "Changed (1) · Bob 1\n  2026-11-02  Bob  shop:t-3f2a1b4c  Ship the export.  (priority: none → high)\n"
        in out
    )
    assert out.endswith(
        "Removed (1) · Bob 1\n  2026-11-08  Bob  shop:t-55161023  Write the docs.\n"
    )


def test_json_filtered_by_event_author_and_field(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = changes_repo(tmp_path / "shop")
    assert main(["changes", str(root), *DAYS, "--json", "--event", "closed,reopened,started"]) == 0
    entries = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [(e["event"], e["author"], e["key"]) for e in entries] == [
        ("reopened", "Bob", ID),
        ("closed", "Ana", ID),
        ("started", "Ana", ID),
    ]
    assert (
        main(["changes", str(root), *DAYS, "--json", "--author", "bob", "--field", "priority"]) == 0
    )
    entries = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [(e["subject"], [c["field"] for c in e["changes"]]) for e in entries] == [
        ("Raise", ["priority"])
    ]


def test_the_last_fourteen_days_by_default(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    changes_repo(tmp_path / "shop")
    assert main(["changes", str(tmp_path / "shop")]) == 0
    first = capsys.readouterr().out.splitlines()[0]
    assert first.startswith("tadu changes: ")
    assert " to " in first


def test_refusals_and_problems(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["changes", str(tmp_path), "--since", "2026-11-20", "--until", "2026-11-10"]) == 2
    assert capsys.readouterr().err == "tadu changes: since 2026-11-20 is after until 2026-11-10\n"
    assert main(["changes", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err.startswith("tadu changes: ")
    assert main(["changes", str(tmp_path), *DAYS]) == 0
    captured = capsys.readouterr()
    assert captured.out == "tadu changes: 2026-11-01 to 2026-11-30 · no change\n"
    assert captured.err.startswith(f"tadu changes: {tmp_path.name}: not a git repository")
