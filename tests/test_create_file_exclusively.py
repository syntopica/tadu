from pathlib import Path

import pytest

from tadu.create_file_exclusively import create_file_exclusively


def test_creates_the_file_and_leaves_no_temp_file(tmp_path: Path) -> None:
    create_file_exclusively(tmp_path / "TODO.md", "# TODO\n")
    assert (tmp_path / "TODO.md").read_text() == "# TODO\n"
    assert [path.name for path in tmp_path.iterdir()] == ["TODO.md"]


def test_existing_file_is_never_replaced(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("mine\n")
    with pytest.raises(FileExistsError):
        create_file_exclusively(tmp_path / "TODO.md", "# TODO\n")
    assert (tmp_path / "TODO.md").read_text() == "mine\n"
    assert [path.name for path in tmp_path.iterdir()] == ["TODO.md"]
