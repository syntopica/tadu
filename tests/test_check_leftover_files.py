import tempfile
from pathlib import Path

from tadu.check_leftover_files import check_leftover_files

TASK = "t-55161023-f3a9-43a3-94df-589ca752fa13.json"


def leftovers(root: Path) -> list[tuple[str, str, str, int]]:
    return [
        (f.code, f.severity, Path(f.path).relative_to(root).as_posix(), f.line)
        for f in check_leftover_files(root)
    ]


def test_a_clean_repository_has_none(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    assert check_leftover_files(tmp_path) == ()


def test_temporary_copies_of_the_root_files_are_reported(tmp_path: Path) -> None:
    for name in ("TODO.md", "TODO_LOG.md", "AGENTS.md", "CLAUDE.md"):
        (tmp_path / f".{name}.k2_9xq0a.tmp").write_text("partial")
    assert leftovers(tmp_path) == [
        ("I001", "warning", ".AGENTS.md.k2_9xq0a.tmp", 0),
        ("I001", "warning", ".CLAUDE.md.k2_9xq0a.tmp", 0),
        ("I001", "warning", ".TODO.md.k2_9xq0a.tmp", 0),
        ("I001", "warning", ".TODO_LOG.md.k2_9xq0a.tmp", 0),
    ]
    finding = check_leftover_files(tmp_path)[0]
    assert finding.message == (
        "a temporary file of a tadu write that stopped halfway; delete it, or let the next "
        "tadu write to its folder remove it"
    )


def test_the_name_tempfile_really_gives_is_matched(tmp_path: Path) -> None:
    _, name = tempfile.mkstemp(dir=tmp_path, prefix=".TODO.md.", suffix=".tmp")
    assert leftovers(tmp_path) == [("I001", "warning", Path(name).name, 0)]


def test_other_temporary_files_are_not_tadus(tmp_path: Path) -> None:
    for name in (".README.md.k2_9xq0a.tmp", ".TODO.md.short.tmp", ".TODO.md.K2_9XQ0A.tmp"):
        (tmp_path / name).write_text("not ours")
    (tmp_path / "TODO.md.k2_9xq0a.tmp").write_text("not hidden")
    (tmp_path / "todo").mkdir()
    (tmp_path / "todo" / ".notes.txt.k2_9xq0a.tmp").write_text("not a task")
    assert check_leftover_files(tmp_path) == ()


def test_temporary_task_and_config_files_anywhere_under_todo(tmp_path: Path) -> None:
    for folder in ("todo", "todo/open", "todo/closed", "todo/archive/2025/03"):
        (tmp_path / folder).mkdir(parents=True)
    (tmp_path / "todo" / ".tadu.json.abcdefgh.tmp").write_text("{")
    (tmp_path / "todo" / "open" / f".{TASK}.a1b2c3d4.tmp").write_text("{")
    (tmp_path / "todo" / "closed" / f".{TASK}.zzzzzzzz.tmp").write_text("{")
    (tmp_path / "todo" / "archive" / "2025" / "03" / f".{TASK}.0_0_0_0_.tmp").write_text("{")
    (tmp_path / "todo" / "open" / TASK).write_text("{}")
    assert [path for _, _, path, _ in leftovers(tmp_path)] == [
        "todo/.tadu.json.abcdefgh.tmp",
        f"todo/archive/2025/03/.{TASK}.0_0_0_0_.tmp",
        f"todo/closed/.{TASK}.zzzzzzzz.tmp",
        f"todo/open/.{TASK}.a1b2c3d4.tmp",
    ]


def test_the_staging_folder_of_a_stopped_migration(tmp_path: Path) -> None:
    (tmp_path / ".todo.migrating" / "open").mkdir(parents=True)
    (tmp_path / ".todo.migrating" / "open" / TASK).write_text("{}")
    findings = check_leftover_files(tmp_path)
    assert leftovers(tmp_path) == [("I001", "warning", ".todo.migrating", 0)]
    assert findings[0].message == (
        "tadu migrate stopped halfway; run it again, which starts over, or delete it"
    )


def test_a_file_named_like_the_staging_folder_is_not_reported(tmp_path: Path) -> None:
    (tmp_path / ".todo.migrating").write_text("a file, not the staging folder")
    assert check_leftover_files(tmp_path) == ()
