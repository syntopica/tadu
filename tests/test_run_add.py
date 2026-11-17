from pathlib import Path

import pytest

from tadu.cli import main

LEGEND = (
    "# TODO\n\n> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`\n"
    "> verified complete · `[-]` obsolete or superseded.\n"
)


def repo(tmp_path: Path, todo: str = LEGEND) -> Path:
    (tmp_path / "TODO.md").write_text(todo)
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n")
    (tmp_path / "AGENTS.md").write_text("x\n")
    assert main(["sync", str(tmp_path), "--write"]) == 0
    return tmp_path


def test_dry_run_shows_the_diff_and_changes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo(tmp_path)
    capsys.readouterr()
    argv = ["add", str(root), "--title", "Pick a carrier.", "--kind", "decision", "--no-id"]
    assert main(argv) == 0
    out = capsys.readouterr().out
    assert "+- [ ] Pick a carrier.\n+\n+  Kind: decision\n" in out
    assert out.endswith("TODO.md:6: would add the item; run again with --write\n")
    assert (root / "TODO.md").read_text() == LEGEND


def test_write_adds_an_id_and_runs_doctor(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo(tmp_path)
    argv = ["add", str(root), "--title", "Key.", "--kind", "waiting", "--due", "2026-11-20"]
    argv += ["--check-on", "2026-11-18", "--not-before", "2026-11-17"]
    argv += ["--category", "Shipping", "--kind", "task", "--note", "Asked support.", "--write"]
    assert main(argv) == 0
    text = (root / "TODO.md").read_text()
    assert "\n## Shipping\n\n- [ ] **Shipping:** Key.\n\n  ID: t-" in text
    assert text.endswith(
        "\n\n  Due: 2026-11-20\n\n  Check on: 2026-11-18\n\n  Not before: 2026-11-17\n\n"
        "  Asked support.\n"
    )
    assert "\n\n  Kind: task\n" in text
    assert capsys.readouterr().out.splitlines()[-1].startswith(f"{root}/TODO.md:8: added t-")
    assert main(["doctor", str(root)]) == 0


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--due", "soon"], "tadu add: Due is not a YYYY-MM-DD date\n"),
        (["--note", " "], "tadu add: arguments must not be blank\n"),
    ],
)
def test_invalid_values_exit_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], argv: list[str], message: str
) -> None:
    assert main(["add", str(tmp_path), "--title", "T", *argv]) == 2
    assert capsys.readouterr().err == message


def test_missing_directory_and_backlog(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["add", str(tmp_path / "none"), "--title", "T"]) == 2
    assert capsys.readouterr().err == f"tadu add: {tmp_path / 'none'}: not a directory\n"
    assert main(["add", str(tmp_path), "--title", "T"]) == 2
    assert "missing; start the backlog with `tadu init`" in capsys.readouterr().err


def test_refusals_leave_the_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root = repo(tmp_path, LEGEND + "\n```\nopen fence\n")
    assert main(["add", str(root), "--title", "T", "--write"]) == 2
    assert "a fence is left open; refused" in capsys.readouterr().err
    (root / "TODO.md").write_text(LEGEND)
    monkeypatch.setattr("tadu.plan_add.introduced_errors", lambda *_: ["T003"])
    assert main(["add", str(root), "--title", "T", "--write"]) == 2
    assert "would add doctor errors T003; refused" in capsys.readouterr().err
    assert (root / "TODO.md").read_text() == LEGEND


def test_a_file_changed_before_the_write_is_kept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = repo(tmp_path)
    monkeypatch.setattr("tadu.run_todo_change.write_if_unchanged", lambda *_: False)
    assert main(["add", str(root), "--title", "T", "--write"]) == 2
    assert (root / "TODO.md").read_text() == LEGEND
