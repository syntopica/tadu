from pathlib import Path

import pytest

from tadu.run_doctor import run_doctor


def test_exit_one_and_json_lines(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_doctor((str(tmp_path),), True) == 1
    out = capsys.readouterr().out.splitlines()
    assert any('"code": "T001"' in line for line in out)
