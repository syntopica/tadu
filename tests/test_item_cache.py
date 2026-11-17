import json
from datetime import date
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

import tadu.cached_folder_items
import tadu.cached_payloads
from tadu.item_record import item_record
from tadu.read_task_file import read_task_file
from tadu.read_task_items import read_task_items
from tadu.record_item import record_item
from tadu.task_item import task_item

RELATED = "t-00000009-0000-4000-8000-000000000009"


@pytest.fixture
def trusting(monkeypatch: pytest.MonkeyPatch) -> None:
    """Treat files written a moment ago as old enough to cache."""
    monkeypatch.setattr(tadu.cached_payloads, "RACY_NANOSECONDS", -(10**12))


def shop(tmp_path: Path) -> Path:
    tasks = [
        sample_task(1, due="2026-12-01", labels=["ui"], blocked_by=[RELATED], started="2026-11-02"),
        sample_task(2, "done", closed="2026-11-10"),
        sample_task(3, "cancelled", closed="2020-01-01"),
    ]
    return task_backlog(tmp_path / "shop", tasks)


def titles(root: Path, cutoff: date = date.min) -> list[str]:
    return [item.title for item in read_task_items(root, ".", cutoff)]


def test_record_round_trip(tmp_path: Path) -> None:
    root = shop(tmp_path)
    file = read_task_file(next((root / "todo" / "open").iterdir()))
    item = task_item(file, root)
    assert record_item(json.loads(json.dumps(item_record(item)))) == item


def test_record_of_another_shape_raises() -> None:
    with pytest.raises(TypeError):
        record_item({"not": "a list"})
    with pytest.raises(ValueError, match="not enough values"):
        record_item([1, 2])


@pytest.mark.usefixtures("trusting")
def test_unchanged_files_come_from_the_cache(
    tmp_path: Path, private_item_cache: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = shop(tmp_path)
    assert titles(root) == ["Task 1", "Task 2", "Task 3"]
    assert len(list(private_item_cache.iterdir())) == 2  # open/ and closed/
    monkeypatch.setattr(tadu.cached_folder_items, "fresh_cache_entry", None)  # no file is read
    assert titles(root) == ["Task 1", "Task 2", "Task 3"]
    assert titles(root, date(2026, 11, 1)) == ["Task 1", "Task 2"]


@pytest.mark.usefixtures("trusting")
def test_edits_and_deletions_are_seen(tmp_path: Path) -> None:
    root = shop(tmp_path)
    titles(root)
    path = next((root / "todo" / "open").iterdir())
    path.write_text(path.read_text().replace('"Task 1"', '"Task one, renamed"'))
    (root / "todo" / "closed" / f"{sample_task(2)['id']}.json").unlink()
    assert titles(root) == ["Task one, renamed", "Task 3"]


def test_recent_files_are_read_but_not_cached(tmp_path: Path, private_item_cache: Path) -> None:
    root = shop(tmp_path)
    assert titles(root) == ["Task 1", "Task 2", "Task 3"]
    assert list(private_item_cache.iterdir()) == []


@pytest.mark.usefixtures("trusting")
def test_a_damaged_or_foreign_cache_is_ignored(tmp_path: Path, private_item_cache: Path) -> None:
    root = shop(tmp_path)
    titles(root)
    for cache in private_item_cache.iterdir():
        cache.write_text("{not json")
    assert titles(root) == ["Task 1", "Task 2", "Task 3"]
    contents: tuple[object, ...] = (
        {"version": 0, "entries": {}},
        {"version": 1, "entries": []},
        [],
    )
    for content in contents:
        for cache in private_item_cache.iterdir():
            cache.write_text(json.dumps(content))
        assert titles(root) == ["Task 1", "Task 2", "Task 3"]


@pytest.mark.usefixtures("trusting")
def test_an_entry_with_a_broken_record_is_read_again(
    tmp_path: Path, private_item_cache: Path
) -> None:
    root = shop(tmp_path)
    titles(root)
    for cache in private_item_cache.iterdir():
        data = json.loads(cache.read_text())
        for number, entry in enumerate(data["entries"].values()):
            entry[1] = [["short"], "not a list", [*entry[1][:2], ["broken"]]][number % 3]
        cache.write_text(json.dumps(data))
    assert titles(root) == ["Task 1", "Task 2", "Task 3"]


@pytest.mark.usefixtures("trusting")
def test_a_broken_record_of_a_file_now_unreadable_is_dropped(
    tmp_path: Path, private_item_cache: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = shop(tmp_path)
    titles(root)
    for cache in private_item_cache.iterdir():
        data = json.loads(cache.read_text())
        for entry in data["entries"].values():
            entry[1] = ["short"]
        cache.write_text(json.dumps(data))
    monkeypatch.setattr(tadu.cached_folder_items, "fresh_cache_entry", lambda *_: None)
    assert titles(root) == []


def test_unreadable_files_are_skipped_and_other_files_ignored(tmp_path: Path) -> None:
    root = shop(tmp_path)
    (root / "todo" / "open" / "t-bad.json").write_text("{")
    (root / "todo" / "open" / "notes.txt").write_text("x")
    assert titles(root) == ["Task 1", "Task 2", "Task 3"]


@pytest.mark.usefixtures("trusting")
def test_a_cache_that_cannot_be_written_is_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("")
    monkeypatch.setenv("TADU_CACHE_DIR", str(blocker / "cache"))
    assert titles(shop(tmp_path)) == ["Task 1", "Task 2", "Task 3"]
    assert blocker.read_text() == ""


@pytest.mark.usefixtures("trusting")
def test_no_cache_when_disabled(
    tmp_path: Path, private_item_cache: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TADU_NO_CACHE", "1")
    assert titles(shop(tmp_path)) == ["Task 1", "Task 2", "Task 3"]
    assert list(private_item_cache.iterdir()) == []
