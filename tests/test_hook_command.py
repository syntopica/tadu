import io
from pathlib import Path

import pytest

from tadu.hook_command import hook_command


def stdin(monkeypatch: pytest.MonkeyPatch, data: bytes) -> None:
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(data), encoding="utf-8"))


def test_prints_only_when_there_is_something_to_say(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    stdin(monkeypatch, b"{}")
    assert hook_command() == 0
    assert capsys.readouterr().out == ""
    (tmp_path / "TODO.md").write_text("- [x] stray\n")
    payload = f'{{"tool_name": "Edit", "tool_input": {{"file_path": "{tmp_path / "TODO.md"}"}}}}'
    stdin(monkeypatch, payload.encode())
    assert hook_command() == 0
    assert "T003" in capsys.readouterr().out


def test_undecodable_input_is_silent(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    stdin(monkeypatch, b"\xff")
    assert hook_command() == 0
    assert capsys.readouterr().out == ""
