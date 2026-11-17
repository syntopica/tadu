from pathlib import Path

import pytest

from tadu.read_todo_text import read_todo_text


def test_reads_the_exact_text(tmp_path: Path) -> None:
    path = tmp_path / "TODO.md"
    path.write_bytes(b"# TODO\r\n")
    assert read_todo_text(path) == "# TODO\r\n"


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (None, "missing; start the backlog with `tadu init`"),
        (b"\xff", "not valid UTF-8"),
        (b"a\r\nb\n", "irregular line endings; normalise the file first"),
    ],
)
def test_refusals(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], content: bytes | None, message: str
) -> None:
    path = tmp_path / "TODO.md"
    if content is not None:
        path.write_bytes(content)
    assert read_todo_text(path) is None
    assert message in capsys.readouterr().err
