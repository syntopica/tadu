import json
from pathlib import Path

import pytest
from attention_repo import attention_repo

from tadu.cli import main


def test_tasks_first_and_what_is_left_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = attention_repo(tmp_path)
    assert main(["next", str(repo)]) == 0
    out, err = capsys.readouterr()
    assert out == (
        "shop:TODO.md:1 [backlog] urgent Fix payments.\nshop:TODO.md:17 [backlog] - Ana's page.\n"
    )
    assert err == (
        "tadu next: not for an agent alone: 1 to decide, 1 to chase, 1 blocked"
        " (`tadu inbox` lists what waits on a person now)\n"
    )


def test_workspace_me_leaves_others_tasks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    attention_repo(tmp_path)
    assert main(["next", "--workspace", str(tmp_path), "--json"]) == 0
    out, err = capsys.readouterr()
    assert [json.loads(line)["title"] for line in out.splitlines()] == ["Fix payments."]
    assert "1 to chase, 3 assigned to others (" in err


def test_nothing_to_do_says_so(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = attention_repo(tmp_path, "- [ ] Pick.\n\n  Kind: decision\n")
    assert main(["next", str(repo)]) == 0
    assert capsys.readouterr().err.startswith(
        "tadu next: nothing an agent can do alone; not for an agent alone: 1 to decide ("
    )
    (repo / "TODO.md").write_text("# TODO\n")
    assert main(["next", str(repo)]) == 0
    assert capsys.readouterr() == ("", "tadu next: nothing an agent can do alone\n")


def test_all_done_and_nothing_else_is_silent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = attention_repo(tmp_path, "- [ ] Only.\n")
    assert main(["next", str(repo)]) == 0
    assert capsys.readouterr() == ("shop:TODO.md:1 [backlog] - Only.\n", "")


def test_bad_scope_exits_two(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    for command in ("next", "inbox", "urgent"):
        assert main([command, "--workspace", str(tmp_path / "none")]) == 2
        assert capsys.readouterr().err.startswith(f"tadu {command}: ")


def test_an_item_not_started_yet_is_counted_apart(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = attention_repo(tmp_path, "- [ ] Renew the domain.\n\n  Not before: 2999-01-01\n")
    assert main(["next", str(repo)]) == 0
    out, err = capsys.readouterr()
    assert out == ""
    assert err == (
        "tadu next: nothing an agent can do alone; not for an agent alone: 1 not before a "
        "later date (`tadu inbox` lists what waits on a person now)\n"
    )
