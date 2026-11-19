"""tadu migrate --recover brings into a migrated backlog, from git, what an older migrate lost."""

import json
from pathlib import Path

import pytest
from old_migration import REAL_IDS, commit, git, lost_lines, needs_git, old_repo, tasks

from tadu.cli import main

pytestmark = needs_git


def test_ids_fields_text_and_headers_come_back(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    assert lost_lines(root) != []
    assert main(["doctor", str(root)]) == 1
    assert capsys.readouterr().out.count("warning J022") == 3
    assert main(["migrate", str(root), "--recover"]) == 0
    assert "(dry run: add --write)" in capsys.readouterr().out
    assert git(root, "status", "--porcelain") == ""
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    capsys.readouterr()
    assert lost_lines(root) == []
    found = tasks(root)
    assert {title: found[title]["id"] for title in REAL_IDS} == REAL_IDS
    assert found["Switch to live carrier rates"]["kind"] == "waiting"
    assert main(["doctor", str(root)]) == 0
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    assert "already recovered from" in capsys.readouterr().out


def test_work_done_since_the_migration_stays(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    lost = str(tasks(root)["Export the lock"]["id"])
    follow = ["add", str(root), "--title", "Follow up", "--related", lost, "--priority", "normal"]
    assert main([*follow, "--write"]) == 0
    deleted = next((root / "todo" / "open").glob("t-7837082b*.json"))
    deleted.unlink()
    edited = next((root / "todo" / "open").glob("t-14635936*.json"))
    edited.write_text(json.dumps({**json.loads(edited.read_text()), "priority": "normal"}))
    commit(root, "work since")
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    capsys.readouterr()
    found = tasks(root)
    assert "Switch to live carrier rates" not in found
    assert found["Follow up"]["related"] == [REAL_IDS["Export the lock"]]
    rust = found["Maybe rewrite the CLI in Rust"]
    assert rust["priority"] == "normal"
    assert isinstance(rust["notes"], list)
    assert rust["notes"][-2:] == ["Priority: low", "Priority: high"]


@pytest.mark.parametrize("lost", ["t-47296e7f", "t-3b651131"], ids=["open", "closed, no notes"])
def test_a_recovery_that_stopped_midway_is_finished(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], lost: str
) -> None:
    root = old_repo(tmp_path)
    unlink = Path.unlink

    def stop(path: Path, *, missing_ok: bool = False) -> None:
        if path.name.startswith(lost):  # a task under the id it lost, once its copy is written
            raise KeyboardInterrupt
        unlink(path, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", stop)
    with pytest.raises(KeyboardInterrupt):
        main(["migrate", str(root), "--recover", "--write"])
    monkeypatch.undo()
    assert "x-format-1-recovered" not in (root / "todo" / "tadu.json").read_text()
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    assert "(already written; the old file goes)" in capsys.readouterr().out
    assert {title: tasks(root)[title]["id"] for title in REAL_IDS} == REAL_IDS
    assert "x-format-1-recovered" in (root / "todo" / "tadu.json").read_text()
    assert main(["doctor", str(root)]) == 0


def test_an_explicit_revision_and_the_refusals(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    before = git(root, "rev-parse", "HEAD^").strip()
    assert main(["migrate", str(root), "--recover", "--from", before, "--write"]) == 0
    assert lost_lines(root) == []
    assert main(["migrate", str(root), "--recover", "--from", "HEAD"]) == 2
    assert "HEAD has no TODO.md or TODO_LOG.md; give --from REV" in capsys.readouterr().err
    assert main(["migrate", str(root), "--from", before]) == 2
    assert "--from goes with --recover" in capsys.readouterr().err
    assert main(["migrate", str(root / "todo"), "--recover"]) == 2
    assert "not a task backlog; nothing to recover" in capsys.readouterr().err
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / "todo").mkdir(parents=True)
    (elsewhere / "todo" / "tadu.json").write_text((root / "todo" / "tadu.json").read_text())
    assert main(["migrate", str(elsewhere), "--recover"]) == 2
    assert "no commit deleted TODO.md; give --from REV" in capsys.readouterr().err


def test_the_migration_commit_is_found_past_a_later_hand_made_todo_md(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = old_repo(tmp_path)
    (root / "TODO.md").write_text("# TODO\n\n- [ ] Written by hand after the migration.\n")
    commit(root, "a TODO.md by hand")
    (root / "TODO.md").unlink()
    commit(root, "and removed")
    assert main(["migrate", str(root), "--recover", "--write"]) == 0
    capsys.readouterr()
    assert {title: tasks(root)[title]["id"] for title in REAL_IDS} == REAL_IDS
    assert "Written by hand after the migration" not in tasks(root)


def test_a_markdown_backlog_that_is_not_utf8_is_named_so(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    git(tmp_path, "init", "-q")
    (tmp_path / "TODO.md").write_bytes(b"# TODO\n\n- [ ] Caf\xe9.\n")
    commit(tmp_path, "latin-1 backlog")
    (tmp_path / "TODO.md").unlink()
    assert main(["init", str(tmp_path), "--format", "2", "--write"]) == 0
    commit(tmp_path, "migrated by hand")
    capsys.readouterr()
    assert main(["migrate", str(tmp_path), "--recover"]) == 2
    assert "a backlog file is not UTF-8 text; convert it, then give --from" in (
        capsys.readouterr().err
    )
