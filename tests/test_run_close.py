from datetime import date
from pathlib import Path

import pytest

from tadu.closing import Closing
from tadu.run_close import run_close

CLOSING = Closing("x", "pytest green", None, None, None, date(2026, 10, 19))
LOG = "# Log\n\n<!-- tadu:log v1 since 2026-10-01 -->\n"


def backlog(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n## UI\n\n- [ ] fix header\n- [ ] other\n")
    (tmp_path / "TODO_LOG.md").write_text(LOG)


def test_dry_run_prints_and_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    backlog(tmp_path)
    assert run_close(str(tmp_path), "fix header", CLOSING, write=False) == 0
    assert "+- [x] 2026-10-19 — **UI:** fix header" in capsys.readouterr().out
    assert (tmp_path / "TODO_LOG.md").read_text() == LOG


def test_write_moves_the_item(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    backlog(tmp_path)
    assert run_close(str(tmp_path), "fix header", CLOSING, write=True) == 0
    capsys.readouterr()
    assert "fix header" not in (tmp_path / "TODO.md").read_text()
    assert "  - Evidence: pytest green\n" in (tmp_path / "TODO_LOG.md").read_text()


def test_crlf_files_stay_crlf(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_bytes(b"# TODO\r\n\r\n- [ ] fix header\r\n")
    (tmp_path / "TODO_LOG.md").write_bytes(LOG.replace("\n", "\r\n").encode())
    assert run_close(str(tmp_path), "fix", CLOSING, write=True) == 0
    capsys.readouterr()
    assert b"\n" not in (tmp_path / "TODO_LOG.md").read_bytes().replace(b"\r\n", b"")


def test_refusals_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_close(str(tmp_path), "fix", CLOSING, write=True) == 2
    backlog(tmp_path)
    assert run_close(str(tmp_path), "nothing", CLOSING, write=True) == 2
    capsys.readouterr()


def test_failed_write_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    backlog(tmp_path)
    monkeypatch.setattr("tadu.run_close.write_closed_backlog", lambda *_args: False)
    assert run_close(str(tmp_path), "fix header", CLOSING, write=True) == 2
    capsys.readouterr()


def test_root_that_is_not_a_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_close(str(tmp_path / "absent"), "fix", CLOSING, write=False) == 2
    assert "not a directory" in capsys.readouterr().err


@pytest.mark.parametrize("tail", ["more detail", "closing` code span"])
def test_lazy_continuation_refuses_without_writing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], tail: str
) -> None:
    todo = f"# TODO\n\n- [ ] target\n  continued `open\n{tail}\n\n- [ ] keep\n"
    (tmp_path / "TODO.md").write_text(todo)
    (tmp_path / "TODO_LOG.md").write_text(LOG)
    assert run_close(str(tmp_path), "target", CLOSING, write=True) == 2
    assert "continuation" in capsys.readouterr().err
    assert (tmp_path / "TODO.md").read_text() == todo
    assert (tmp_path / "TODO_LOG.md").read_text() == LOG


def test_backtick_info_prose_does_not_refuse_close(tmp_path: Path) -> None:
    todo = "# TODO\n\n- [ ] target\n  ```a`b\n\n- [ ] keep\n"
    (tmp_path / "TODO.md").write_text(todo)
    (tmp_path / "TODO_LOG.md").write_text(LOG)
    assert run_close(str(tmp_path), "target", CLOSING, write=True) == 0
    assert "```a`b" in (tmp_path / "TODO_LOG.md").read_text()
    assert "```a`b" not in (tmp_path / "TODO.md").read_text()
    assert "- [ ] keep" in (tmp_path / "TODO.md").read_text()
