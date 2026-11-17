import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main

TODAY = datetime.now(UTC).astimezone().date()


def day(offset: int) -> str:
    return (TODAY + timedelta(days=offset)).isoformat()


def ident(number: int) -> str:
    return str(sample_task(number)["id"])


def shop(tmp_path: Path) -> Path:
    tasks = [
        sample_task(
            1, priority="high", category="ui", type="bug", due=day(3), notes=["Safari only."]
        ),
        sample_task(2, priority="urgent", category="api", due=day(-2), milestone="v1"),
        sample_task(3, priority="low", category="ui", type="docs"),
        sample_task(4, "blocked", blocked_by=[ident(1)], title="Waits on task 1"),
        sample_task(5, priority="untriaged", defer_until=day(5), title="Later"),
        sample_task(6, "done", closed=day(-30), title="Fix the Safari crash in the toolbar"),
        sample_task(7, "done", closed=day(-1), duplicate_of=None, discovered_from=ident(1)),
    ]
    return task_backlog(tmp_path / "shop", tasks)


def out(capsys: pytest.CaptureFixture[str], *argv: str) -> list[str]:
    assert main(list(argv)) == 0
    return capsys.readouterr().out.splitlines()


def test_list_lines_and_queries(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = str(shop(tmp_path))
    assert out(capsys, "list", root, "--category", "ui") == [
        f"shop:t-00000001 [backlog] high due {day(3)} Task 1",
        "shop:t-00000003 [backlog] low Task 3",
    ]
    assert out(capsys, "list", root, "--type", "docs,bug", "--min-priority", "high") == [
        f"shop:t-00000001 [backlog] high due {day(3)} Task 1"
    ]
    assert out(capsys, "list", root, "--milestone", "v1") == [
        f"shop:t-00000002 [backlog] urgent due {day(-2)} Task 2"
    ]
    assert out(capsys, "list", root, "--text", "safari") == [
        f"shop:t-00000001 [backlog] high due {day(3)} Task 1"
    ]
    assert len(out(capsys, "list", root, "--due-within", "7")) == 2
    assert out(capsys, "list", root, "--overdue") == [
        f"shop:t-00000002 [backlog] urgent due {day(-2)} Task 2"
    ]
    assert len(out(capsys, "list", root, "--history", "--column", "done")) == 2
    assert len(out(capsys, "list", root)) == 6
    assert len(out(capsys, "list", root, "--open")) == 5
    with pytest.raises(SystemExit):
        main(["list", root, "--open", "--history"])


def test_sort_and_pages(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = str(shop(tmp_path))
    assert [line.split()[2] for line in out(capsys, "list", root, "--sort", "priority")][:3] == [
        "urgent",
        "high",
        "-",
    ]
    assert out(capsys, "list", root, "--sort", "due")[0].endswith("Task 2")
    assert out(capsys, "list", root, "--history", "--column", "done", "--sort", "closed")[
        0
    ].endswith("Task 7")
    assert main(["list", root, "--limit", "2", "--offset", "1"]) == 0
    captured = capsys.readouterr()
    assert len(captured.out.splitlines()) == 2
    assert (
        "tadu list: showing 2-3 of 6; 3 more: add --offset 3, or narrow the filter" in captured.err
    )
    assert len(out(capsys, "list", root, "--limit", "0")) == 6
    rows = [json.loads(line) for line in out(capsys, "list", root, "--json", "--category", "api")]
    assert (rows[0]["category"], rows[0]["milestone"], rows[0]["type"]) == ("api", "v1", "feature")


def test_show_by_prefix_with_reverse_relations(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = str(shop(tmp_path))
    lines = out(capsys, "show", "t-00000001", root, "--done-days", "99")
    assert lines[0] == "{"
    assert "blocks: shop:t-00000004 [blocked] normal Waits on task 1" in lines
    assert "discovered: shop:t-00000007 [done] normal Task 7" in lines
    shown = json.loads(out(capsys, "show", "t-00000001", root, "--json")[0])
    assert shown["key"] == ident(1)


def test_show_refuses_an_ambiguous_or_unknown_prefix(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    twins = [
        sample_task(1, id="t-abcdef12-0000-4000-8000-000000000001"),
        sample_task(2, id="t-abcdef12-0000-4000-8000-000000000002"),
    ]
    root = str(task_backlog(tmp_path, twins))
    assert main(["show", "t-abcdef12", root]) == 1
    assert (
        "is ambiguous: t-abcdef12-0000-4000-8000-000000000001, t-abcdef12"
        in capsys.readouterr().err
    )
    assert main(["show", "t-9999", root]) == 1
    assert "no item t-9999" in capsys.readouterr().err
    assert out(capsys, "list", root)[0].startswith(
        f"{tmp_path.name}:t-abcdef12-0000-4000-8000-000000000001 "
    )


def test_ready(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = str(shop(tmp_path))
    assert out(capsys, "ready", root) == [
        f"shop:t-00000002 [backlog] urgent due {day(-2)} Task 2",
        f"shop:t-00000001 [backlog] high due {day(3)} Task 1",
        "shop:t-00000003 [backlog] low Task 3",
    ]
    assert main(["ready", root, "--limit", "1"]) == 0
    assert "tadu ready: showing 1-1 of 3" in capsys.readouterr().err
    assert (
        json.loads(out(capsys, "ready", root, "--json", "--limit", "1")[0])["priority"] == "urgent"
    )
    assert main(["ready", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err.startswith("tadu ready: ")


def test_similar(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = str(shop(tmp_path))
    lines = out(capsys, "similar", "Fix the Safari crashes in the toolbar", root)
    assert lines[0] == "1.00 shop:t-00000006 [done] normal Fix the Safari crash in the toolbar"
    assert out(capsys, "similar", "Fix the Safari crashes in the toolbar", root, "--open") == []
    assert out(capsys, "similar", "the of a", root) == []
    assert main(["similar", "x", "--workspace", str(tmp_path)]) == 2
    assert capsys.readouterr().err.startswith("tadu similar: ")
