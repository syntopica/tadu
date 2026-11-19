"""A close run again after it stopped between writing TODO_LOG.md and TODO.md."""

from datetime import date
from pathlib import Path

import pytest

from tadu.closing import Closing
from tadu.run_close import run_close

UID = "t-55161023-f3a9-43a3-94df-589ca752fa13"
HEAD = "# TODO Log\n\n<!-- tadu:log v1 since 2026-01-01 -->\n\n## 2026\n\n### 2026-11\n\n"
TODO = f"# TODO\n\n`[ ]` `[~]` `[!]` `[x]` `[-]`\n\n- [ ] Fix the header.\n\n  ID: {UID}\n"
SAME_DAY = date(2026, 11, 18)


def done(proof: str = "tests pass", result: str | None = None) -> Closing:
    return Closing("x", proof, result, None, None, SAME_DAY)


def stopped(tmp_path: Path, entry: str, todo: str = TODO) -> Path:
    """The files as a close leaves them when it stops after writing the log."""
    (tmp_path / "TODO.md").write_text(todo)
    (tmp_path / "TODO_LOG.md").write_text(HEAD + entry)
    return tmp_path


LOGGED = (
    f"- [x] 2026-11-18 — **General:** Fix the header.\n\n  ID: {UID}\n  - Evidence: tests pass\n"
)


def finish(root: Path, closing: Closing, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    status = run_close(str(root), "Fix the header", closing, write=True)
    return status, capsys.readouterr().err


def test_the_same_close_again_removes_the_item_and_logs_nothing_twice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, LOGGED)
    assert finish(root, done(), capsys) == (0, "")
    assert UID not in (root / "TODO.md").read_text()
    assert (root / "TODO_LOG.md").read_text() == HEAD + LOGGED


def test_new_evidence_and_a_first_result_are_added_and_the_record_kept(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    todo = TODO + "\n  Found on the pricing page.\n"
    root = stopped(tmp_path, LOGGED, todo)
    assert finish(root, done("CI run 812 green", "The logo shows"), capsys) == (0, "")
    assert (root / "TODO_LOG.md").read_text() == HEAD + (
        f"- [x] 2026-11-18 — **General:** Fix the header.\n\n  ID: {UID}\n"
        "  Found on the pricing page.\n  - Result: The logo shows\n"
        "  - Evidence: tests pass\n  - Evidence: CI run 812 green\n"
    )


def test_an_entry_without_a_proof_line_is_completed_at_its_end(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, f"- [x] 2026-11-18 — Fix the header.\n\n  ID: {UID}\n")
    assert finish(root, done(), capsys)[0] == 0
    assert (root / "TODO_LOG.md").read_text().endswith(f"  ID: {UID}\n  - Evidence: tests pass\n")


@pytest.mark.parametrize(
    "case",
    [
        (
            LOGGED,
            Closing("-", "not needed", None, None, None, SAME_DAY),
            (
                "already closed as [x] at TODO_LOG.md:9 by a close that stopped halfway; "
                "run the close again with --evidence to finish it"
            ),
        ),
        (
            f"- [-] 2026-11-18 — Fix the header.\n\n  ID: {UID}\n  - Resolution: dropped\n",
            done(),
            (
                "already closed as [-] at TODO_LOG.md:9 by a close that stopped halfway; "
                "run the close again with --resolution to finish it"
            ),
        ),
        (
            f"- [-] 2026-11-18 — Fix the header.\n\n  ID: {UID}\n  - Resolution: dropped\n",
            Closing("-", "superseded", None, None, None, SAME_DAY),
            (
                "already closed at TODO_LOG.md:9 with 'Resolution: dropped' by a close that "
                "stopped halfway; run the close again with that value to finish it"
            ),
        ),
        (
            LOGGED.replace("  - Evidence", "  - Result: Logo back\n  - Evidence"),
            done(result="Logo is back"),
            (
                "already closed at TODO_LOG.md:9 with 'Result: Logo back' by a close that "
                "stopped halfway; run the close again with that value to finish it"
            ),
        ),
    ],
)
def test_another_state_result_or_resolution_is_refused_and_nothing_written(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], case: tuple[str, Closing, str]
) -> None:
    entry, closing, refusal = case
    root = stopped(tmp_path, entry)
    assert finish(root, closing, capsys) == (2, f"{root / 'TODO.md'}:5: {refusal}\n")
    assert (root / "TODO.md").read_text() == TODO
    assert (root / "TODO_LOG.md").read_text() == HEAD + entry


def test_an_item_without_an_id_is_closed_as_before(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, LOGGED, "# TODO\n\n- [ ] Fix the header.\n")
    assert finish(root, done(), capsys) == (0, "")
    assert (root / "TODO_LOG.md").read_text().count("Fix the header.") == 2


def test_a_close_run_again_another_day_keeps_that_day_too(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = stopped(tmp_path, LOGGED)
    later = Closing("x", "tests pass", None, None, None, date(2026, 11, 20))
    assert finish(root, later, capsys) == (0, "")
    assert (root / "TODO_LOG.md").read_text() == HEAD + LOGGED + "  - Close run again: 2026-11-20\n"
