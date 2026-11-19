"""A close stopped between its two writes (Ctrl-C, a kill, a crash) is what doctor reports."""

from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

import tadu.write_closed_backlog
from tadu.cli import main
from tadu.hook_report import hook_report
from tadu.write_file_atomically import write_file_atomically

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"


def stop_at_second_write(monkeypatch: pytest.MonkeyPatch) -> None:
    """Let the first atomic write through, then stop the command as Ctrl-C would."""
    written: list[Path] = []

    def write_once(target: Path, text: str) -> None:
        if written:
            raise KeyboardInterrupt
        write_file_atomically(target, text)
        written.append(target)

    monkeypatch.setattr(tadu.write_closed_backlog, "write_file_atomically", write_once)


def test_a_markdown_close_stopped_after_the_log_is_t005_and_finished_by_a_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "TODO.md").write_text(
        f"# TODO\n\n`[ ]` `[~]` `[!]` `[x]` `[-]`\n\n- [ ] Fix the header.\n\n  ID: {UID}\n"
    )
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n")
    (tmp_path / "AGENTS.md").write_text("<!-- tadu:rule v5 -->\n<!-- /tadu:rule -->\n")
    close = ["close", str(tmp_path), "--match", "Fix the header", "--evidence", "tests pass"]
    stop_at_second_write(monkeypatch)
    with pytest.raises(KeyboardInterrupt):
        main([*close, "--write"])
    monkeypatch.undo()
    assert UID in (tmp_path / "TODO.md").read_text()
    assert UID in (tmp_path / "TODO_LOG.md").read_text()
    capsys.readouterr()
    assert main(["doctor", str(tmp_path)]) == 1
    assert f"TODO.md:7: error T005 ID {UID} is already closed" in capsys.readouterr().out
    assert "T005" in (hook_report(tmp_path, 20) or "")
    assert main([*close, "--write"]) == 0
    out = capsys.readouterr().out
    assert "already logged at TODO_LOG.md:9 by a close that stopped halfway; finishing it" in out
    assert UID not in (tmp_path / "TODO.md").read_text()
    assert (tmp_path / "TODO_LOG.md").read_text().count(UID) == 1
    assert main(["doctor", str(tmp_path)]) == 0


def test_a_task_close_stopped_before_the_open_file_is_deleted_is_j007_and_finished(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1)])

    def stop(*_: object, **__: object) -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(Path, "unlink", stop)
    with pytest.raises(KeyboardInterrupt):
        main(["close", str(root), "--id", str(sample_task(1)["id"]), "--evidence", "e", "--write"])
    monkeypatch.undo()
    capsys.readouterr()
    assert main(["doctor", str(root)]) == 1
    out = capsys.readouterr().out
    assert "error J007 id also used by" in out
    assert "again to finish it" in out
    assert "J007" in (hook_report(root, 20) or "")
    assert main(["close", str(root), "--match", "Task 1", "--evidence", "e", "--write"]) == 0
    assert "finished the stopped close of" in capsys.readouterr().out
    assert main(["doctor", str(root)]) == 0
