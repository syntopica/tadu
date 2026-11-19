from pathlib import Path

from tadu.working_text import working_text


def test_lines_joined_and_absent_file(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_bytes(b"- [ ] A.\r\n\r\n  B.\r\n")
    assert working_text(tmp_path / "TODO.md") == "- [ ] A.\n\n  B."
    assert working_text(tmp_path / "TODO_LOG.md") == ""
