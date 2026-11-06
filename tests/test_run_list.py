import json
from pathlib import Path

import pytest

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


def view_workspace(tmp_path: Path) -> Path:
    root = repo(tmp_path)
    space = tmp_path / "space"
    space.mkdir()
    (space / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[view]]\nname = "hot"\npriority = "high"\n'
    )
    (space / "tadu-workspace.local.toml").write_text(f'version = 1\n[paths]\nshop = "{root}"\n')
    return space


def test_view_selects_saved_filter(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    space = str(view_workspace(tmp_path))
    assert main(["list", "--workspace", space, "--view", "hot"]) == 0
    assert capsys.readouterr().out == "shop:TODO.md:1 [backlog] high A.\n"


def test_flag_overrides_view(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    space = str(view_workspace(tmp_path))
    assert main(["list", "--workspace", space, "--view", "hot", "--priority", "low"]) == 0
    assert capsys.readouterr().out == ""


def test_unknown_view_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    space = str(view_workspace(tmp_path))
    assert main(["list", "--workspace", space, "--view", "cold"]) == 2
    assert capsys.readouterr().err == "tadu list: unknown view cold (known: hot)\n"


def test_view_without_workspace_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["list", str(repo(tmp_path)), "--view", "hot"]) == 2
    assert capsys.readouterr().err == "tadu list: --view needs --workspace\n"
