import argparse
from datetime import date
from pathlib import Path

import pytest

from tadu.doctor_command import doctor_command


def _args(paths: list[str], workspace: str | None) -> argparse.Namespace:
    return argparse.Namespace(paths=paths, workspace=workspace, json=False)


def test_neither_paths_nor_workspace_exits_two(capsys: pytest.CaptureFixture[str]) -> None:
    assert doctor_command(_args([], None), date(2026, 11, 4)) == 2
    assert capsys.readouterr().err == "tadu doctor: give repository paths or --workspace\n"


def test_workspace_only_runs(tmp_path: Path) -> None:
    assert doctor_command(_args([], str(tmp_path)), date(2026, 11, 4)) == 1
