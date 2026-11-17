from pathlib import Path

import pytest

from tadu.rule_block_text import rule_block_text
from tadu.run_sync import run_sync


def test_an_edit_made_while_syncing_is_kept(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Rules\n")

    def edit_then_serve() -> str:
        agents.write_text("# Rules\n\nAn edit made meanwhile.\n")
        return rule_block_text()

    monkeypatch.setattr("tadu.run_sync.rule_block_text", edit_then_serve)
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 2
    assert agents.read_text() == "# Rules\n\nAn edit made meanwhile.\n"
    assert "changed since tadu read it; nothing written, run again" in capsys.readouterr().err
