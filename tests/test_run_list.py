import json
from datetime import UTC, datetime
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


def test_view_selects_a_saved_filter_and_flags_win(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo(tmp_path)
    (tmp_path / "tadu-workspace.toml").write_text(
        'version = 1\n[[repository]]\nkey = "shop"\n[[view]]\nname = "hot"\npriority = "high"\n'
    )
    (tmp_path / "tadu-workspace.local.toml").write_text('version = 1\n[paths]\nshop = "shop"\n')
    workspace = ["list", "--workspace", str(tmp_path), "--view", "hot"]
    assert main(workspace) == 0
    assert capsys.readouterr().out == "shop:TODO.md:1 [backlog] high A.\n"
    assert main([*workspace, "--priority", "low"]) == 0
    assert capsys.readouterr().out == ""
    assert main([*workspace[:-1], "cold"]) == 2
    assert capsys.readouterr().err == "tadu list: unknown view cold (views: hot)\n"


def test_view_without_workspace_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["list", str(repo(tmp_path)), "--view", "hot"]) == 2
    assert capsys.readouterr().err == "tadu list: --view needs --workspace\n"


def test_kind_filter(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "shop"
    root.mkdir()
    (root / "TODO.md").write_text(
        "- [ ] Fix it.\n\n- [ ] Pick a carrier.\n\n  Kind: decision\n\n"
        "- [!] Carrier key from Ana.\n\n  Kind: waiting\n\n  Due: 2026-11-20\n"
    )
    assert main(["list", str(root)]) == 0
    assert capsys.readouterr().out == (
        "shop:TODO.md:1 [backlog] - Fix it.\n"
        "shop:TODO.md:3 [backlog/decision] - Pick a carrier.\n"
        "shop:TODO.md:7 [blocked/waiting] - Carrier key from Ana.\n"
    )
    assert main(["list", str(root), "--kind", "waiting", "--json"]) == 0
    [line] = capsys.readouterr().out.splitlines()
    assert (json.loads(line)["kind"], json.loads(line)["due"]) == ("waiting", "2026-11-20")


def test_open_leaves_out_what_closed_today(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo(tmp_path)
    today = datetime.now(UTC).astimezone().date().isoformat()
    (root / "TODO_LOG.md").write_text(f"- [x] {today} — **C:** Did.\n  - Evidence: e\n")
    assert main(["list", str(root), "--done-days", "0"]) == 0
    assert "[done]" in capsys.readouterr().out
    assert main(["list", str(root), "--open"]) == 0
    assert capsys.readouterr().out == (
        "shop:TODO.md:1 [backlog] high A.\nshop:TODO.md:5 [backlog] - B.\n"
    )


def test_unclassified_and_check_before(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "shop"
    root.mkdir()
    (root / "TODO.md").write_text(
        "- [ ] Old item.\n\n- [ ] Look again.\n\n  Kind: later\n\n  Check on: 2026-11-20\n\n"
        "- [ ] A task.\n\n  Kind: task\n\n  Not before: 2026-12-01\n"
    )
    assert main(["list", str(root), "--kind", "unclassified"]) == 0
    assert capsys.readouterr().out == "shop:TODO.md:1 [backlog] - Old item.\n"
    assert main(["list", str(root), "--check-before", "2026-11-21"]) == 0
    assert capsys.readouterr().out == "shop:TODO.md:3 [backlog/later] - Look again.\n"
    assert main(["list", str(root), "--kind", "task", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert (data["kind"], data["not_before"], data["check_on"]) == ("task", "2026-12-01", None)
    assert main(["list", str(root), "--kind", "unclassified", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["kind"] is None
