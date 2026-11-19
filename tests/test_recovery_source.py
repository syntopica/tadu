from pathlib import Path

import pytest

from tadu import recovery_source as module
from tadu.history_error import HistoryError
from tadu.recovery_source import recovery_source


def test_unreadable_archive_years_fall_back_to_the_two_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def fail(*_args: object) -> tuple[str, ...]:
        message = "no years"
        raise HistoryError(message)

    def output(_root: Path, *args: str) -> bytes | None:
        return b"abc\n" if args[0] == "rev-parse" else b"text"

    monkeypatch.setattr(module, "log_archive_years_at", fail)
    monkeypatch.setattr(module, "git_output", output)
    assert recovery_source(tmp_path, "HEAD") == ("abc", {"TODO.md": "text", "TODO_LOG.md": "text"})
