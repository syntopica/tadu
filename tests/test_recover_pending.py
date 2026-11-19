"""A recovery that has not finished is never silent: doctor reports it until a run finishes it."""

import json
from pathlib import Path

import pytest
from old_migration import REAL_IDS, commit, git, needs_git, old_repo, tasks

from tadu.cli import main
from tadu.mark_recovery import mark_recovery
from tadu.pending_recovery import PENDING_KEY, pending_recovery
from tadu.recovered_commits import RECOVERED_KEY

pytestmark = needs_git


def config(root: Path) -> dict[str, object]:
    found: dict[str, object] = json.loads((root / "todo" / "tadu.json").read_text())
    return found


def doctor_says(root: Path, capsys: pytest.CaptureFixture[str]) -> str:
    capsys.readouterr()
    main(["doctor", str(root)])
    return capsys.readouterr().out


def test_a_refused_recovery_stays_pending_and_doctor_says_so(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    source = git(root, "rev-parse", "HEAD^").strip()
    assert main(["migrate", str(root), "--recover"]) == 0
    assert PENDING_KEY not in config(root)
    real = REAL_IDS["Decide the retry policy"]
    taken = root / "todo" / "open" / f"{real}.json"
    taken.write_text(
        json.dumps({**tasks(root)["Decide the retry policy"], "id": real, "title": "Else"})
    )
    assert main(["migrate", str(root), "--recover", "--write"]) == 2
    assert config(root)[PENDING_KEY] == source
    assert (
        f"warning C005 tadu migrate --recover from {source[:12]} started and has not finished"
        in doctor_says(root, capsys)
    )
    taken.unlink()
    commit(root, "sorted out the conflict")
    assert main(["migrate", str(root), "--recover", "--from", "HEAD~2"]) == 0
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    assert PENDING_KEY not in config(root)
    assert config(root)[RECOVERED_KEY] == [source]
    assert "C005" not in doctor_says(root, capsys)


def test_a_recovery_stopped_anywhere_after_it_started_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    monkeypatch.setattr("tadu.complete_migration.apply_completion", lambda *_: False)
    assert main(["migrate", str(root), "--recover", "--write"]) == 2
    monkeypatch.undo()
    assert "C005" in doctor_says(root, capsys)
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    assert "C005" not in doctor_says(root, capsys)


def test_another_recovery_waits_until_the_pending_one_is_finished(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    other = "0" * 40
    assert mark_recovery(root / "todo", other) is None
    assert pending_recovery(root / "todo") == other
    assert main(["migrate", str(root), "--recover", "--write"]) == 2
    assert capsys.readouterr().err == (
        f"tadu migrate: the recovery from {other[:12]} has not finished; run it first "
        f"(--from {other})\n"
    )


def test_a_tadu_json_that_cannot_take_the_mark(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    monkeypatch.setattr("tadu.mark_recovery.backlog_unchanged", lambda *_: False)
    assert main(["migrate", str(root), "--recover", "--write"]) == 2
    assert "tadu.json: changed meanwhile; run again" in capsys.readouterr().err
    monkeypatch.undo()
    (root / "todo" / "tadu.json").write_text("{")
    assert str(mark_recovery(root / "todo", "0" * 40)).startswith(
        f"{root / 'todo' / 'tadu.json'}: not valid ("
    )
    assert pending_recovery(root / "todo") is None
    (root / "todo" / "tadu.json").write_text("[]")
    assert main(["migrate", str(root), "--recover", "--write"]) == 2
    assert "tadu.json: not valid" in capsys.readouterr().err
