from pathlib import Path

from tadu.resolve_inside_root import resolve_inside_root


def test_file_under_root_resolves(tmp_path: Path) -> None:
    assert resolve_inside_root(tmp_path / "AGENTS.md", tmp_path) == tmp_path.resolve() / "AGENTS.md"


def test_parent_traversal_is_refused(tmp_path: Path) -> None:
    assert resolve_inside_root(tmp_path / ".." / "x.md", tmp_path) is None


def test_symlink_to_outside_is_refused(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "notes.md").write_text("x")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "AGENTS.md").symlink_to(outside / "notes.md")
    assert resolve_inside_root(root / "AGENTS.md", root) is None


def test_symlink_inside_root_resolves_to_its_target(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("x")
    (tmp_path / "AGENTS.md").symlink_to(tmp_path / "CLAUDE.md")
    assert resolve_inside_root(tmp_path / "AGENTS.md", tmp_path) == tmp_path.resolve() / "CLAUDE.md"
