import json
import subprocess
import sys
from pathlib import Path

import pytest
from closed_pipe import ClosedPipe

from tadu.cli import main


def repo(tmp_path: Path) -> Path:
    root = tmp_path / "shop"
    root.mkdir()
    (root / "TODO.md").write_text("- [ ] A.\n\n  Priority: high\n\n- [ ] B.\n")
    return root


def test_json_one_line_per_item(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list", str(repo(tmp_path)), "--json"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [json.loads(line)["title"] for line in lines] == ["A.", "B."]


def test_priority_filter_and_line_format(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["list", str(repo(tmp_path)), "--priority", "high"]) == 0
    assert capsys.readouterr().out == "shop:TODO.md:1 [backlog] high A.\n"


def test_problems_to_stderr_exit_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    gone = tmp_path / "gone"
    assert main(["list", str(gone), "--json"]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("tadu list: gone: ")


def test_bad_workspace_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err.startswith("tadu list: ")


def test_paths_with_workspace_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list", "x", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err == "tadu list: give repository paths or --workspace, not both\n"


def test_done_days_window(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repo(tmp_path)
    (root / "TODO_LOG.md").write_text(
        "## 2020\n\n### 2020-01\n\n- [x] 2020-01-02 — **C:** Did.\n  - Evidence: e\n"
    )
    assert main(["list", str(root), "--column", "done"]) == 0
    assert capsys.readouterr().out == ""
    assert main(["list", str(root), "--column", "done", "--done-days", "99999"]) == 0
    assert "[done]" in capsys.readouterr().out


def test_reader_closing_early_is_quiet(tmp_path: Path) -> None:
    root = tmp_path / "big"
    root.mkdir()
    # Enough output to overflow the pipe buffer, so writes fail once the reader closes.
    (root / "TODO.md").write_text("".join(f"- [ ] Item {n}.\n\n" for n in range(400)))
    command = [sys.executable, "-m", "tadu.cli", "list", str(root), "--json"]
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:  # noqa: S603
        assert process.stdout is not None
        assert process.stderr is not None
        assert json.loads(process.stdout.readline())["title"] == "Item 0."
        process.stdout.close()
        err = process.stderr.read()
    assert process.returncode == 0
    assert err == b""


def test_broken_pipe_exits_zero_in_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with (tmp_path / "out").open("w") as target:
        monkeypatch.setattr(sys, "stdout", ClosedPipe(target.fileno()))
        assert main(["list", str(repo(tmp_path)), "--json"]) == 0
