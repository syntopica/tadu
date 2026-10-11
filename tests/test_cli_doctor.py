from pathlib import Path

from tadu.cli import main


def test_doctor_on_an_empty_directory_exits_one(tmp_path: Path) -> None:
    assert main(["doctor", str(tmp_path)]) == 1
