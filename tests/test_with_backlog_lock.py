"""A task backlog's writing commands take the repository lock format 1 commands take."""

import contextlib
import io
import json
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from sample_task import sample_task
from task_backlog import task_backlog

from tadu.cli import main
from tadu.with_backlog_lock import with_backlog_lock

HOLD = """
import fcntl, os, sys, time
descriptor = os.open(sys.argv[1], os.O_RDONLY)
fcntl.flock(descriptor, fcntl.LOCK_EX)
print("locked", flush=True)
time.sleep(1.5)
"""
ID = str(sample_task(1)["id"])


def test_a_command_waits_for_the_lock_another_process_holds(tmp_path: Path) -> None:
    pytest.importorskip("fcntl")
    root = task_backlog(tmp_path, [sample_task(1)])
    with subprocess.Popen(  # noqa: S603 - this interpreter, a script of this test
        [sys.executable, "-c", HOLD, str(root)], stdout=subprocess.PIPE, text=True
    ) as holder:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "locked"
        started = time.monotonic()
        with contextlib.redirect_stdout(io.StringIO()):
            assert main(["set", ID, "priority=high", "--root", str(root), "--write"]) == 0
        waited = time.monotonic() - started
    assert waited > 0.5
    assert (
        json.loads(next((root / "todo" / "open").glob("*.json")).read_text())["priority"] == "high"
    )


@pytest.mark.parametrize(
    "argv",
    [
        ["add", "{root}", "--title", "New", "--write"],
        ["set", ID, "priority=high", "--root", "{root}", "--write"],
        ["claim", ID, "--as", "bob", "--root", "{root}", "--write"],
        ["close", "{root}", "--id", ID, "--evidence", "ok", "--write"],
        ["fmt", "{root}", "--write"],
        ["archive", "{root}", "--write"],
        ["migrate", "{root}", "--write"],
    ],
    ids=lambda argv: argv[0],
)
def test_every_writing_command_of_a_task_backlog_takes_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, argv: list[str]
) -> None:
    root = task_backlog(tmp_path, [sample_task(1)])
    locked: list[Path] = []

    @contextlib.contextmanager
    def record(path: Path) -> Iterator[None]:
        locked.append(path)
        yield

    monkeypatch.setattr("tadu.with_backlog_lock.backlog_lock", record)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        main([part.replace("{root}", str(root)) for part in argv])
    assert locked == [root]


def test_a_root_that_is_not_a_directory_runs_unlocked(tmp_path: Path) -> None:
    assert with_backlog_lock(str(tmp_path / "missing"), lambda: 7) == 7
