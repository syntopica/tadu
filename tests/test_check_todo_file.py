from pathlib import Path

from tadu.check_todo_file import check_todo_file


def test_missing_file_is_t001(tmp_path: Path) -> None:
    assert [f.code for f in check_todo_file(tmp_path)] == ["T001"]


def test_closed_marker_is_t003_with_line(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        "# TODO\n\n> States: `[ ]` pending · `[~]` partial · `[!]` blocked · `[x]` done · `[-]` obsolete\n\n- [ ] open\n- [x] done\n"
    )
    findings = check_todo_file(tmp_path)
    assert [(f.code, f.line) for f in findings] == [("T003", 6)]


def test_no_legend_is_t002(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text("# TODO\n\n- [ ] open\n")
    assert [f.code for f in check_todo_file(tmp_path)] == ["T002"]


def test_indented_closed_step_under_open_parent_is_not_flagged(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        "# TODO\n\n> States: `[ ]` pending · `[~]` partial · `[!]` blocked · `[x]` done · `[-]` obsolete\n\n- [ ] parent\n  - [x] step\n"
    )
    assert check_todo_file(tmp_path) == ()
