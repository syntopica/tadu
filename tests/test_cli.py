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


def test_sync_prints_the_diff_without_writing(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# A\n")
    assert main(["sync", str(tmp_path)]) == 0
    assert (tmp_path / "AGENTS.md").read_text() == "# A\n"


def test_init_writes_the_backlog(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path), "--write"]) == 0
    assert (tmp_path / "TODO.md").is_file()
    assert (tmp_path / "TODO_LOG.md").is_file()
