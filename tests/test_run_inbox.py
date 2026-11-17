import json
from pathlib import Path

import pytest
from attention_repo import attention_repo

from tadu.cli import main


def test_sections_for_the_person(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = attention_repo(tmp_path)
    assert main(["inbox", str(repo), "--person", "ana"]) == 0
    out, err = capsys.readouterr()
    assert out == (
        "Decide: choices a person must make\n"
        "shop:TODO.md:5 [backlog/decision] - Pick a carrier.\n"
        "\n"
        "Chase: waiting on others, follow-up due\n"
        "shop:TODO.md:11 [backlog/waiting] - Carrier key.\n"
        "\n"
        "Blocked: tasks that cannot go on\n"
        "shop:TODO.md:21 [blocked] - Go live.\n"
    )
    assert err == "tadu inbox: `tadu next` lists 2 task(s) an agent can do alone\n"


def test_workspace_me_and_json_sections(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    attention_repo(tmp_path)
    assert main(["inbox", "--workspace", str(tmp_path), "--json"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert [(json.loads(line)["section"], json.loads(line)["title"]) for line in lines] == [
        ("chase", "Carrier key."),
    ]


def test_empty_inbox_says_so(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = attention_repo(tmp_path, "# TODO\n")
    assert main(["inbox", str(repo)]) == 0
    assert capsys.readouterr() == ("", "tadu inbox: nothing waits on a person\n")
    assert main(["inbox", str(repo), "--person", "ana"]) == 0
    assert capsys.readouterr().err == "tadu inbox: nothing waits on ana\n"
