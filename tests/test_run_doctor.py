import json
from pathlib import Path

import pytest

from tadu.run_doctor import run_doctor


def test_exit_one_and_json_lines(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_doctor((str(tmp_path),), True) == 1
    out = capsys.readouterr().out.splitlines()
    assert any('"code": "T001"' in line for line in out)


def test_undecodable_file_is_e001_and_the_other_checks_and_roots_still_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "TODO.md").write_bytes(b"# TODO \xff\n")
    (bad / "AGENTS.md").write_text("# A\n")
    empty = tmp_path / "empty"
    empty.mkdir()
    assert run_doctor((str(bad), str(empty)), True) == 1
    findings = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    codes = [(f["code"], f["path"]) for f in findings]
    assert ("E001", str(bad / "TODO.md")) in codes
    assert ("R003", str(bad / "AGENTS.md")) in codes
    assert ("T001", str(empty / "TODO.md")) in codes
    message = next(f["message"] for f in findings if f["code"] == "E001")
    assert message.startswith(f"{bad / 'TODO.md'} could not be read: not valid UTF-8")


def test_warnings_only_exit_zero(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n`[ ]` `[~]` `[!]` `[x]` `[-]`\n")
    (tmp_path / "AGENTS.md").write_text("<!-- tadu:rule v0 -->\nx\n<!-- /tadu:rule -->\n")
    assert run_doctor((str(tmp_path),), False) == 0


def test_empty_backlog_exits_one(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("")
    assert run_doctor((str(tmp_path),), False) == 1
