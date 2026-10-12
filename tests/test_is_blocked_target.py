from pathlib import Path

from tadu.is_blocked_target import is_blocked_target


def test_missing_path_is_not_blocked(tmp_path: Path) -> None:
    assert not is_blocked_target(tmp_path / "TODO.md")


def test_regular_file_is_not_blocked(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    assert not is_blocked_target(tmp_path / "TODO.md")


def test_directory_is_blocked(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").mkdir()
    assert is_blocked_target(tmp_path / "TODO.md")


def test_dangling_symlink_is_blocked(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").symlink_to(tmp_path / "absent.md")
    assert is_blocked_target(tmp_path / "TODO.md")
