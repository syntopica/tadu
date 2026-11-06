import os
import subprocess
import sys
from pathlib import Path

import pytest

from tadu.quiet_broken_pipe import quiet_broken_pipe


def test_status_passes_through() -> None:
    assert quiet_broken_pipe(lambda: 3) == 3


def test_closed_reader_ends_quietly(monkeypatch: pytest.MonkeyPatch) -> None:
    moved: list[tuple[int, int]] = []
    monkeypatch.setattr(os, "dup2", lambda source, target: moved.append((source, target)))

    def broken() -> int:
        raise BrokenPipeError

    assert quiet_broken_pipe(broken) == 0
    assert len(moved) == 1
    assert moved[0][1] == sys.stdout.fileno()


def test_list_into_a_reader_that_stops_early(tmp_path: Path) -> None:
    lines = "".join(f"- [ ] Item {n}.\n\n" for n in range(2000))
    (tmp_path / "TODO.md").write_text(f"# TODO\n\n{lines}")
    command = [sys.executable, "-m", "tadu.cli", "list", str(tmp_path)]
    with subprocess.Popen(  # noqa: S603
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as process:
        assert process.stdout is not None
        assert process.stdout.readline()
        process.stdout.close()
        assert process.stderr is not None
        errors = process.stderr.read()
    assert process.returncode == 0
    assert b"Traceback" not in errors
