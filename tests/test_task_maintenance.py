import json
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main

CONFIG = {"tadu": 2, "categories": {"core": "Core"}}


def ident(number: int) -> str:
    return str(sample_task(number)["id"])


def files(root: Path, folder: str) -> list[str]:
    return sorted(
        p.relative_to(root / "todo" / folder).as_posix()
        for p in (root / "todo" / folder).rglob("*.json")
    )


def test_archive_without_a_policy_moves_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1, "done", closed="2020-01-01")])
    assert main(["archive", str(root), "--write"]) == 0
    assert "no archive policy in todo/tadu.json" in capsys.readouterr().out
    assert files(root, "closed") == [f"{ident(1)}.json"]


def test_archive_by_age_and_by_count_with_month_folders_only_when_busy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    quiet = [sample_task(n, "done", closed=f"2023-{n:02d}-15") for n in range(1, 13)]
    busy = [
        sample_task(100 + n, "done", closed=f"2025-0{1 + n % 2}-{1 + n:02d}") for n in range(20)
    ]
    recent = [sample_task(300 + n, "done", closed=f"2999-01-0{1 + n}") for n in range(3)]
    policy = {**CONFIG, "archive": {"after_days": 30, "keep_closed": 2}}
    root = task_backlog(tmp_path, [*quiet, *busy, *recent], policy)
    assert main(["archive", str(root)]) == 0
    assert "33 move(s) (dry run: add --write)" in capsys.readouterr().out
    assert len(files(root, "closed")) == 35
    assert main(["archive", str(root), "--write"]) == 0
    assert files(root, "closed") == [f"{ident(301)}.json", f"{ident(302)}.json"]
    archived = files(root, "archive")
    assert f"2023/{ident(1)}.json" in archived
    assert f"2025/01/{ident(100)}.json" in archived
    assert f"2999/{ident(300)}.json" in archived
    assert main(["archive", str(root)]) == 0
    assert "0 move(s)" in capsys.readouterr().out


def test_archive_regroups_a_year_that_became_busy(tmp_path: Path) -> None:
    policy = {**CONFIG, "archive": {"after_days": 1, "month_folders_min": 2}}
    root = task_backlog(tmp_path, [sample_task(1, "done", closed="2024-03-01")], policy)
    assert main(["archive", str(root), "--write"]) == 0
    assert files(root, "archive") == [f"2024/{ident(1)}.json"]
    for number in (2, 3):
        path = root / "todo" / "closed" / f"{ident(number)}.json"
        path.write_text(json.dumps(sample_task(number, "done", closed="2024-03-02")))
    assert main(["archive", str(root), "--write"]) == 0
    assert files(root, "archive") == [f"2024/03/{ident(n)}.json" for n in (1, 2, 3)]


def test_archive_refusals(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["archive", str(tmp_path)]) == 2
    root = task_backlog(tmp_path, [])
    (root / "todo" / "tadu.json").write_text("{")
    assert main(["archive", str(root)]) == 2
    assert "not JSON" in capsys.readouterr().err


def test_fmt(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = task_backlog(tmp_path, [sample_task(1), sample_task(2)])
    messy = root / "todo" / "open" / f"{ident(1)}.json"
    messy.write_text(json.dumps(dict(reversed(sample_task(1).items()))))
    assert main(["fmt", str(root)]) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"todo/open/{ident(1)}.json",
        "tadu fmt: would rewrite 1 file(s) (dry run: add --write)",
    ]
    assert main(["fmt", str(root), "--write"]) == 0
    assert json.loads(messy.read_text()) == sample_task(1)
    assert main(["fmt", str(root)]) == 0
    assert capsys.readouterr().out.endswith("tadu fmt: would rewrite 0 file(s)\n")
    assert main(["fmt", str(tmp_path / "none")]) == 2


def test_init_format_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["init", str(tmp_path), "--format", "2"]) == 0
    assert not (tmp_path / "todo").exists()
    assert main(["init", str(tmp_path), "--format", "2", "--write"]) == 0
    config = json.loads((tmp_path / "todo" / "tadu.json").read_text())
    assert config == {"tadu": 2, "categories": {"general": "General"}}
    assert "<!-- tadu:rule v4 -->" in (tmp_path / "AGENTS.md").read_text()
    capsys.readouterr()
    assert main(["doctor", str(tmp_path)]) == 0


def test_init_format_2_refusals(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    assert main(["init", str(tmp_path), "--format", "2"]) == 2
    assert "run tadu migrate to convert it" in capsys.readouterr().err
    other = tmp_path / "other"
    other.mkdir()
    (other / "todo").write_text("a file")
    assert main(["init", str(other), "--format", "2"]) == 2
    assert "not a regular file" in capsys.readouterr().err
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "AGENTS.md").write_text("<!-- tadu:rule v4 -->\nno close\n")
    assert main(["init", str(bad), "--format", "2", "--write"]) == 2
    assert not (bad / "todo").exists()


def test_archive_by_count_only_and_tidy_folders(tmp_path: Path) -> None:
    tasks = [sample_task(n, "done", closed=f"2026-10-0{n}") for n in range(1, 4)]
    root = task_backlog(tmp_path, tasks, {**CONFIG, "archive": {"keep_closed": 2}})
    misplaced = root / "todo" / "archive" / "2022" / f"{ident(9)}.json"
    misplaced.parent.mkdir(parents=True)
    misplaced.write_text(json.dumps(sample_task(9, "done", closed="2023-05-05")))
    assert main(["archive", str(root), "--write"]) == 0
    assert files(root, "closed") == [f"{ident(2)}.json", f"{ident(3)}.json"]
    assert files(root, "archive") == [f"2023/{ident(9)}.json", f"2026/{ident(1)}.json"]
    assert not (root / "todo" / "archive" / "2022").exists()
