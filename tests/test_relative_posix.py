from pathlib import Path

import pytest

from tadu.relative_posix import relative_posix


def test_path_under_the_base() -> None:
    assert relative_posix(Path("/r/todo/open/t.json"), Path("/r")) == "todo/open/t.json"


def test_relative_path_under_the_current_directory() -> None:
    assert relative_posix(Path("todo/open/t.json"), Path()) == "todo/open/t.json"


def test_a_path_outside_the_base_is_refused_as_relative_to_does() -> None:
    with pytest.raises(ValueError, match="is not in the subpath"):
        relative_posix(Path("/elsewhere/t.json"), Path("/r"))
