import os
import time
from pathlib import Path

import pytest

from tadu.clean_stale_temporaries import clean_stale_temporaries
from tadu.cli import main
from tadu.create_file_exclusively import create_file_exclusively
from tadu.leftover_patterns import CACHE_TEMPORARY, REPOSITORY_TEMPORARY, STALE_SECONDS
from tadu.remove_stale_temporaries import remove_stale_temporaries
from tadu.write_file_atomically import write_file_atomically
from tadu.write_item_cache import write_item_cache

TASK = "t-55161023-f3a9-43a3-94df-589ca752fa13.json"


def aged(path: Path, seconds: float = 2 * STALE_SECONDS + 5) -> Path:
    path.write_text("partial")
    then = time.time() - seconds
    os.utime(path, (then, then))
    return path


def test_only_old_temporary_files_of_tadus_own_are_removed(tmp_path: Path) -> None:
    stale = aged(tmp_path / ".TODO.md.k2_9xq0a.tmp")
    task = aged(tmp_path / f".{TASK}.a1b2c3d4.tmp")
    fresh = aged(tmp_path / ".TODO_LOG.md.zzzzzzzz.tmp", seconds=1)
    other = aged(tmp_path / ".notes.md.k2_9xq0a.tmp")
    folder = tmp_path / ".AGENTS.md.abcdefgh.tmp"
    folder.mkdir()
    remove_stale_temporaries(tmp_path, REPOSITORY_TEMPORARY)
    assert not stale.exists()
    assert not task.exists()
    assert fresh.exists()
    assert other.exists()
    assert folder.is_dir()


def test_a_folder_is_scanned_once_per_period(tmp_path: Path) -> None:
    now = int(time.time() // STALE_SECONDS)
    clean_stale_temporaries(tmp_path, REPOSITORY_TEMPORARY, now)
    later = aged(tmp_path / ".TODO.md.k2_9xq0a.tmp")
    clean_stale_temporaries(tmp_path, REPOSITORY_TEMPORARY, now)
    assert later.exists()
    clean_stale_temporaries(tmp_path, REPOSITORY_TEMPORARY, now + 1)
    assert not later.exists()


def test_a_missing_folder_or_a_file_that_cannot_go_is_left_alone(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    remove_stale_temporaries(tmp_path / "missing", REPOSITORY_TEMPORARY)
    stuck = aged(tmp_path / ".TODO.md.k2_9xq0a.tmp")

    def refuse(path: str) -> None:
        raise PermissionError(path)

    monkeypatch.setattr(os, "unlink", refuse)
    remove_stale_temporaries(tmp_path, REPOSITORY_TEMPORARY)
    assert stuck.exists()


def test_every_writer_clears_what_killed_writes_left_beside_its_file(tmp_path: Path) -> None:
    for folder in ("replaced", "created", "cache"):
        (tmp_path / folder).mkdir()
    left = [
        aged(tmp_path / "replaced" / ".TODO.md.k2_9xq0a.tmp"),
        aged(tmp_path / "created" / ".TODO_LOG.md.k2_9xq0a.tmp"),
        aged(tmp_path / "cache" / f"items-{'a' * 24}.json.4242.tmp"),
    ]
    write_file_atomically(tmp_path / "replaced" / "TODO.md", "# TODO\n")
    create_file_exclusively(tmp_path / "created" / "TODO_LOG.md", "# TODO Log\n")
    write_item_cache(tmp_path / "cache" / f"items-{'b' * 24}.json", {})
    assert [path.exists() for path in left] == [False, False, False]
    assert CACHE_TEMPORARY.fullmatch(f"checks-{'0' * 24}.json.1.tmp")


def test_init_run_again_clears_what_a_killed_init_left(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    markdown, tasks = tmp_path / "markdown", tmp_path / "tasks"
    markdown.mkdir()
    assert main(["init", str(markdown), "--write"]) == 0
    left = aged(markdown / ".TODO_LOG.md.k2_9xq0a.tmp")
    clean_stale_temporaries.cache_clear()  # as a new process, or a minute later, would find it
    assert main(["init", str(markdown), "--write"]) == 0
    assert not left.exists()
    tasks.mkdir()
    assert main(["init", str(tasks), "--format", "2", "--write"]) == 0
    left = aged(tasks / "todo" / ".tadu.json.k2_9xq0a.tmp")
    clean_stale_temporaries.cache_clear()
    assert main(["init", str(tasks), "--format", "2", "--write"]) == 0
    assert not left.exists()
    capsys.readouterr()


def test_the_same_relative_folder_in_two_places_is_two_folders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    left = []
    for name in ("one", "two"):
        (tmp_path / name).mkdir()
        left.append(aged(tmp_path / name / ".TODO.md.k2_9xq0a.tmp"))
        monkeypatch.chdir(tmp_path / name)
        remove_stale_temporaries(Path(), REPOSITORY_TEMPORARY)
    assert [path.exists() for path in left] == [False, False]
