from pathlib import Path

from tadu.is_inside_root import is_inside_root


def test_file_under_root_is_inside(tmp_path: Path) -> None:
    assert is_inside_root(tmp_path / "AGENTS.md", tmp_path)


def test_parent_traversal_is_outside(tmp_path: Path) -> None:
    assert not is_inside_root(tmp_path / ".." / "x.md", tmp_path)


def test_symlink_to_outside_is_outside(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "notes.md").write_text("x")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "AGENTS.md").symlink_to(outside / "notes.md")
    assert not is_inside_root(root / "AGENTS.md", root)


def test_symlink_inside_root_is_inside(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("x")
    (tmp_path / "AGENTS.md").symlink_to(tmp_path / "CLAUDE.md")
    assert is_inside_root(tmp_path / "AGENTS.md", tmp_path)
