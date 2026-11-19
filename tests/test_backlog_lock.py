import multiprocessing
import sys
import threading
import time
from pathlib import Path

import pytest
from lock_worker import add_under_lock

from tadu.backlog_lock import backlog_lock


@pytest.mark.parametrize("without_flock", [False, True], ids=["flock", "filelock"])
def test_writers_in_other_processes_take_turns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, without_flock: bool
) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    (tmp_path / "counter").write_text("0")
    spawn = multiprocessing.get_context("spawn")
    workers = [
        spawn.Process(
            target=add_under_lock, args=(str(tmp_path), 15), kwargs={"without_flock": without_flock}
        )
        for _ in range(3)
    ]
    for worker in workers:
        worker.start()
    for worker in workers:
        worker.join()
    assert (tmp_path / "counter").read_text() == "45"
    assert [path for path in tmp_path.iterdir() if path.name not in {"counter", "cache"}] == []


def test_without_flock_the_lock_file_lives_in_the_users_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(sys.modules, "fcntl", None)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    order: list[str] = []

    def second() -> None:
        with backlog_lock(tmp_path / "repo"):
            order.append("second")

    (tmp_path / "repo").mkdir()
    with backlog_lock(tmp_path / "repo"):
        thread = threading.Thread(target=second)
        thread.start()
        time.sleep(0.05)
        order.append("first")
    thread.join()
    assert order == ["first", "second"]
    assert [p.suffix for p in (tmp_path / "cache" / "tadu" / "locks").iterdir()] == [".lock"]
    assert list((tmp_path / "repo").iterdir()) == []


def test_second_writer_waits_for_the_first(tmp_path: Path) -> None:
    order: list[str] = []

    def second() -> None:
        with backlog_lock(tmp_path):
            order.append("second")

    with backlog_lock(tmp_path):
        thread = threading.Thread(target=second)
        thread.start()
        time.sleep(0.05)
        order.append("first")
    thread.join()
    assert order == ["first", "second"]
