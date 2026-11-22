"""`tadu board --auth github` on an install without the `github` extra."""

import sys
from pathlib import Path

import pytest
from team_workspace import team_workspace

from tadu.cli import main


def test_signing_in_without_the_extra_names_it_and_stops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # None in sys.modules makes the import fail as a missing library does.
    monkeypatch.setitem(sys.modules, "tadu.prepare_team_board", None)
    argv = ["board", "--workspace", str(team_workspace(tmp_path)), "--port", "0"]
    assert main([*argv, "--auth", "github"]) == 2
    err = capsys.readouterr().err
    assert err.startswith("tadu board: --auth github needs the github extra (")
    assert err.endswith("): install 'tadu[github]'\n")
