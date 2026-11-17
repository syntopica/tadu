from pathlib import Path

import pytest

from tadu.cli import main

TODO = (
    "# TODO\n\n> States: `[ ]` pending · `[~]` partial or unverified · `[!]` blocked · `[x]`\n"
    "> verified complete · `[-]` obsolete or superseded.\n\n"
    "- [ ] Fix payments.\n\n  Priority: urgent\n\n- [ ] Fix the cart.\n"
)


def repo(tmp_path: Path, todo: str = TODO) -> Path:
    (tmp_path / "TODO.md").write_text(todo)
    (tmp_path / "TODO_LOG.md").write_text("# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n")
    return tmp_path


def mark(root: Path, *argv: str) -> int:
    return main(["mark", str(root), "--match", "payments", *argv])


def test_block_then_reopen(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repo(tmp_path)
    assert mark(root, "--state", "blocked", "--note", "Blocked on the decision.") == 0
    assert capsys.readouterr().out.endswith("would set blocked; run again with --write\n")
    assert (root / "TODO.md").read_text() == TODO
    assert mark(root, "--state", "blocked", "--note", "Blocked on the decision.", "--write") == 0
    text = (root / "TODO.md").read_text()
    assert "- [!] Fix payments.\n\n  Priority: urgent\n\n  Blocked on the decision.\n\n" in text
    assert mark(root, "--state", "open", "--write") == 0
    assert "- [ ] Fix payments." in (root / "TODO.md").read_text()
    capsys.readouterr()
    assert mark(root, "--state", "open") == 0
    assert capsys.readouterr().out == f"{root}/TODO.md:6: nothing to change\n"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--state", "blocked"], "--state blocked needs a --note naming the blocker"),
        (["--state", "open", "--note", " "], "arguments must not be blank"),
        (["--state", "open", "--note", "a\nb"], "arguments must be single lines"),
        (["--state", "open", "--note", "Due: 2026-01-01"], "a note cannot start like a field"),
    ],
)
def test_refused_arguments(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], argv: list[str], message: str
) -> None:
    assert mark(repo(tmp_path), *argv) == 2
    assert capsys.readouterr().err.startswith(f"tadu mark: {message}")


def test_refused_targets(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    assert mark(tmp_path / "none", "--state", "open") == 2
    assert capsys.readouterr().err == f"tadu mark: {tmp_path / 'none'}: not a directory\n"
    assert mark(tmp_path, "--state", "open") == 2
    assert "missing; start the backlog with `tadu init`" in capsys.readouterr().err
    root = repo(tmp_path)
    assert main(["mark", str(root), "--match", "Fix", "--state", "open"]) == 2
    assert "2 open items match 'Fix'" in capsys.readouterr().err
    monkeypatch.setattr("tadu.plan_mark.introduced_errors", lambda *_: ["T003"])
    assert mark(root, "--state", "in_progress", "--write") == 2
    assert ":6: would add doctor errors T003; refused" in capsys.readouterr().err
    assert (root / "TODO.md").read_text() == TODO


def test_an_item_opening_an_unclosed_fence_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = repo(tmp_path, "- [ ] Fix payments.\n\n  ```\n  code\n")
    assert mark(root, "--state", "in_progress", "--write") == 2
    assert "opens a fence its indentation does not close" in capsys.readouterr().err


def test_a_file_changed_before_the_write_is_kept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = repo(tmp_path)
    monkeypatch.setattr("tadu.run_todo_change.write_if_unchanged", lambda *_: False)
    assert mark(root, "--state", "in_progress", "--write") == 2
    assert (root / "TODO.md").read_text() == TODO


def test_fields_are_replaced_or_added(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = repo(tmp_path)
    argv = ["--priority", "low", "--kind", "decision", "--due", "2026-12-31"]
    assert mark(root, *argv) == 0
    assert "would set Kind decision; Priority low; Due 2026-12-31" in capsys.readouterr().out
    assert (root / "TODO.md").read_text() == TODO
    assert mark(root, *argv, "--write") == 0
    text = (root / "TODO.md").read_text()
    assert "  Priority: low\n\n  Kind: decision\n\n  Due: 2026-12-31\n\n- [ ] Fix the cart." in text
    assert mark(root, *argv, "--write") == 0
    assert "nothing to change" in capsys.readouterr().out.splitlines()[-1]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        ([], "give --state or a field to set"),
        (["--due", "soon"], "Due is not a YYYY-MM-DD date"),
        (["--estimate", "x"], "Estimate"),
        (["--labels", "a\nb"], "arguments must be single lines"),
    ],
)
def test_refused_fields(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], argv: list[str], message: str
) -> None:
    assert mark(repo(tmp_path), *argv) == 2
    assert message in capsys.readouterr().err
