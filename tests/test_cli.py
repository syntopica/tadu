from pathlib import Path

import pytest

from tadu.cli import main


def test_version_prints_and_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.startswith("tadu ")


def test_doctor_on_an_empty_directory_exits_one(tmp_path: Path) -> None:
    assert main(["doctor", str(tmp_path)]) == 1
