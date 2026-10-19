import io
from pathlib import Path

import pytest

from tadu.hook_command import hook_command


def test_prints_only_when_there_is_something_to_say(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
    assert hook_command() == 0
    assert capsys.readouterr().out == ""
    (tmp_path / "TODO.md").write_text("- [x] stray\n")
    payload = f'{{"tool_name": "Edit", "tool_input": {{"file_path": "{tmp_path / "TODO.md"}"}}}}'
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))
    assert hook_command() == 0
    assert "T003" in capsys.readouterr().out
