from pathlib import Path

from tadu.nearest_backlog_root import nearest_backlog_root


def test_walks_up_to_the_backlog(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n")
    (tmp_path / "src" / "deep").mkdir(parents=True)
    assert nearest_backlog_root(tmp_path / "src" / "deep") == tmp_path


def test_none_without_a_backlog(tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    found = nearest_backlog_root(tmp_path / "empty")
    assert found is None or found not in (tmp_path, tmp_path / "empty")
