"""A recovery is done once per commit: what it brought and was removed since does not come back."""

import json
from pathlib import Path

import pytest
from old_migration import REAL_IDS, commit, git, needs_git, old_repo, tasks

from tadu.cli import main
from tadu.merged_task import KEPT
from tadu.recovered_commits import RECOVERED_KEY, recovered_commits

pytestmark = needs_git


def config(root: Path) -> dict[str, object]:
    found: dict[str, object] = json.loads((root / "todo" / "tadu.json").read_text())
    return found


def test_what_was_removed_after_a_recovery_stays_removed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    assert main(["migrate", str(root), "--recover"]) == 0
    assert RECOVERED_KEY not in config(root)
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    assert config(root)[RECOVERED_KEY] == [git(root, "rev-parse", "HEAD^").strip()]
    commit(root, "recovered")
    next((root / "todo" / "closed").glob("t-9ca231da*.json")).unlink()
    webhook = next(
        (root / "todo" / "open").glob(f"{REAL_IDS['Reject duplicate webhook deliveries']}.json")
    )
    task = json.loads(webhook.read_text())
    assert KEPT in task["notes"]
    webhook.write_text(json.dumps({key: value for key, value in task.items() if key != "notes"}))
    (root / "todo" / "tadu.json").write_text(
        json.dumps(
            {key: value for key, value in config(root).items() if key != "x-format-1-header"}
        )
    )
    commit(root, "removed what I do not want")
    capsys.readouterr()
    for same in ([], ["--from", "HEAD~3"], ["--from", git(root, "rev-parse", "HEAD~3").strip()]):
        assert main(["migrate", str(root), "--recover", *same, "--write"]) == 0
        assert capsys.readouterr().out.startswith("tadu migrate: already recovered from ")
        assert git(root, "status", "--porcelain") == ""
    assert "Legacy migration of the billing module" not in tasks(root)


def test_dropping_the_record_or_another_commit_recovers_again(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    next((root / "todo" / "closed").glob("t-9ca231da*.json")).unlink()
    (root / "todo" / "tadu.json").write_text(
        json.dumps({key: value for key, value in config(root).items() if key != RECOVERED_KEY})
    )
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    assert "Legacy migration of the billing module" in tasks(root)
    first = git(root, "rev-list", "--max-parents=0", "HEAD").strip()
    (root / "TODO.md").write_text(git(root, "show", f"{first}:TODO.md"))
    commit(root, "a TODO.md again, to recover from")
    capsys.readouterr()
    assert main(["migrate", str(root), "--recover", "--from", "HEAD", "--write"]) == 0
    assert "already recovered" not in capsys.readouterr().out
    assert len(recovered_commits(root / "todo")) == 2


def test_a_refused_recovery_is_not_recorded_so_it_can_be_finished(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    real = REAL_IDS["Decide the retry policy"]
    taken = root / "todo" / "open" / f"{real}.json"
    other = {**tasks(root)["Decide the retry policy"], "id": real, "title": "Something else"}
    taken.write_text(json.dumps(other))
    assert main(["migrate", str(root), "--recover", "--write"]) == 2
    assert RECOVERED_KEY not in config(root)
    taken.unlink()
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    capsys.readouterr()
    assert tasks(root)["Decide the retry policy"]["id"] == real
    assert RECOVERED_KEY in config(root)


def test_a_record_that_cannot_be_written_or_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    monkeypatch.setattr("tadu.record_recovery.backlog_unchanged", lambda *_: False)
    assert main(["migrate", str(root), "--recover", "--write"]) == 2
    capsys.readouterr()
    assert RECOVERED_KEY not in config(root)
    (root / "todo" / "tadu.json").write_text(json.dumps({**config(root), RECOVERED_KEY: "x"}))
    assert recovered_commits(root / "todo") == ()
    (root / "todo" / "tadu.json").write_text("{")
    assert recovered_commits(root / "todo") == ()
