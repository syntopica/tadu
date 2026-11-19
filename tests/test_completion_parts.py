import json
import subprocess
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.apply_completion import apply_completion
from tadu.completion_plan import CompletionPlan
from tadu.git_output import git_output
from tadu.header_config_change import HEADER_KEY, header_config_change
from tadu.lacking_lines import lacking_lines
from tadu.load_task_files import load_task_files
from tadu.merged_task import KEPT, merged_task
from tadu.recovered_ids import recovered_ids
from tadu.refused_recoveries import refused_recoveries
from tadu.renamed_task import renamed_task
from tadu.renamed_tasks import renamed_tasks

LOST, REAL, OTHER = (str(sample_task(n)["id"]) for n in (1, 2, 3))


def test_lacking_lines_name_what_a_task_does_not_hold() -> None:
    converted = {
        **sample_task(1, "done", priority="high", labels=["a", "b"], notes=["One.", "", "Two."]),
        "evidence": ["pytest passes", "CI green"],
    }
    held = {**sample_task(1, "done", labels=["a"], notes=["One."]), "links": "not a list"}
    assert lacking_lines(converted, held) == [
        "priority: high",
        "labels: b",
        "Two.",
        "evidence: CI green",
    ]
    assert "links: https://x.test" in lacking_lines(
        {**converted, "links": ["https://x.test"]}, held
    )


def test_a_merge_never_replaces_a_value_and_can_be_repeated() -> None:
    old = {**sample_task(1), "notes": ["Kind: decision", "", "Check on: 2026-12-01", "Own."]}
    item = {
        **sample_task(1, priority="high"),
        "kind": "decision",
        "check_on": "2026-12-01",
        "defer_until": "2026-11-01",
        "notes": ["Depends on: t-x (vendor)"],
    }
    from_git = merged_task(old, item, everything=False)
    assert (from_git["kind"], from_git["check_on"], from_git["priority"]) == (
        "decision",
        "2026-12-01",
        "normal",
    )
    assert from_git["notes"] == ["Own.", "", KEPT, "", "Depends on: t-x (vendor)"]
    everything = merged_task(old, item, everything=True)
    assert everything["notes"] == [
        "Own.",
        "",
        KEPT,
        "",
        "priority: high",
        "defer_until: 2026-11-01",
        "Depends on: t-x (vendor)",
    ]
    assert merged_task(everything, item, everything=True) == everything
    assert merged_task(sample_task(2), sample_task(2), everything=True) == sample_task(2)


def test_the_headers_are_added_to_tadu_json_without_replacing_any(tmp_path: Path) -> None:
    todo = task_backlog(tmp_path, []) / "todo"
    assert header_config_change(todo, {}) is None
    change = header_config_change(todo, {"TODO.md": ["# TODO", "", "> Note."]})
    assert change is not None
    (todo / "tadu.json").write_text(change[2])
    assert json.loads(change[2])[HEADER_KEY] == {"TODO.md": ["# TODO", "", "> Note."]}
    assert header_config_change(todo, {"TODO.md": ["# TODO", "> Note."]}) is None
    grown = header_config_change(todo, {"TODO.md": ["# TODO", "> Other."], "TODO_LOG.md": ["#"]})
    assert grown is not None
    assert json.loads(grown[2])[HEADER_KEY] == {
        "TODO.md": ["# TODO", "", "> Note.", "> Other."],
        "TODO_LOG.md": ["#"],
    }


def test_a_stopped_rename_leaves_a_stale_file_whichever_comes_first(tmp_path: Path) -> None:
    for name in ("a", "b"):
        (tmp_path / name).mkdir()
    first = task_backlog(tmp_path / "a", [sample_task(1), sample_task(2)])
    files = load_task_files(first / "todo")[0]
    current, stale = renamed_tasks(files, {LOST: REAL})
    assert [(old.path.name, path.name) for old, path, _ in stale] == [
        (f"{LOST}.json", f"{REAL}.json")
    ]
    assert current[REAL][0] is files[1]
    current, stale = renamed_tasks(tuple(reversed(files)), {LOST: REAL})
    assert stale[0][0] is files[0]
    assert current[REAL][0] is files[1]


def test_an_ambiguous_or_newer_task_keeps_its_id(tmp_path: Path) -> None:
    root = task_backlog(tmp_path, [{**sample_task(1), "tadu": 3}, sample_task(3)])
    (root / "todo" / "open" / "renamed.json").write_text(json.dumps(sample_task(3)))
    files = load_task_files(root / "todo")[0]
    refused = refused_recoveries(files, {LOST: REAL, OTHER: REAL}, lambda *_: True)
    assert [reason.split(": ", 1)[1] for reason in refused.values()] == [
        f"was {REAL}; written by a newer tadu format",
        f"was {REAL}; fix doctor's J005 or J007 first",
    ]


def test_a_list_the_task_holds_more_of_lacks_nothing() -> None:
    held = sample_task(1, labels=["a", "b"])
    assert lacking_lines(sample_task(1, labels=["a"]), held) == []


def test_ids_are_replayed_and_renamed_with_their_notes() -> None:
    log = f"- [x] 2026-10-10 — Kept.\n\n  ID: {REAL}\n  - Evidence: ok\n- [x] 2026-10-10 — Bare.\n"
    assert list(recovered_ids({"TODO_LOG.md": log}).values()) == [REAL]
    task = {
        **sample_task(1),
        "duplicate_of": LOST,
        "blocked_by": [LOST, 7],
        "notes": ["A.", "", f"ID: {REAL}"],
    }
    assert renamed_task(task, {LOST: REAL}) == {
        **sample_task(1),
        "id": REAL,
        "duplicate_of": REAL,
        "blocked_by": [REAL, 7],
        "notes": ["A."],
    }


def test_git_that_is_missing_or_fails_gives_nothing_and_its_bytes_are_kept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert git_output(tmp_path, "rev-parse", "HEAD") is None
    done = subprocess.CompletedProcess[bytes]([], 0, b"\xff", b"")
    monkeypatch.setattr(subprocess, "run", lambda *_, **__: done)
    assert git_output(tmp_path, "show", "HEAD:./TODO.md") == b"\xff"
    monkeypatch.undo()
    monkeypatch.setenv("PATH", str(tmp_path))
    assert git_output(tmp_path, "status") is None


def test_a_changed_file_or_a_failed_write_stops_a_completion(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1), sample_task(3)])
    files = load_task_files(root / "todo")[0]
    changed = CompletionPlan((), (), ((files[0], "{}"),), None, ())
    files[0].path.write_text("{}")
    assert not apply_completion(changed, ())
    assert "changed since tadu read it" in capsys.readouterr().err
    taken = CompletionPlan(((files[1].path, "{}"),), (), (), None, ())
    assert not apply_completion(taken, ())
    assert "run it again to finish" in capsys.readouterr().err
