import os
from pathlib import Path

import pytest

from tadu.rule_block_text import rule_block_text
from tadu.run_sync import run_sync


def test_dry_run_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "AGENTS.md").write_text("# A\n")
    assert run_sync(str(tmp_path), None, write=False, adopt_legacy=False) == 0
    assert (tmp_path / "AGENTS.md").read_text() == "# A\n"
    assert "+<!-- tadu:rule v3 -->" in capsys.readouterr().out


def test_write_appends_block(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# A\n")
    run_sync(str(tmp_path), None, write=True, adopt_legacy=False)
    assert "<!-- tadu:rule v3 -->" in (tmp_path / "AGENTS.md").read_text()


def test_append_without_trailing_newline_leaves_one_blank_line(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("# A")
    run_sync(str(tmp_path), None, write=True, adopt_legacy=False)
    text = (tmp_path / "AGENTS.md").read_text()
    assert text.startswith("# A\n\n<!-- tadu:rule v3 -->\n")
    assert "\n\n\n" not in text


def test_up_to_date_file_is_reported(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "AGENTS.md").write_text("# A\n")
    run_sync(str(tmp_path), None, write=True, adopt_legacy=False)
    capsys.readouterr()
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 0
    assert "up to date" in capsys.readouterr().out


def test_explicit_file_is_used(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "rules.md").write_text("# R\n")
    run_sync(str(tmp_path), "docs/rules.md", write=True, adopt_legacy=False)
    assert "<!-- tadu:rule v3 -->" in (tmp_path / "docs" / "rules.md").read_text()


def test_symlink_outside_root_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "AGENTS.md").symlink_to(outside)
    assert run_sync(str(root), None, write=True, adopt_legacy=False) == 2
    assert outside.read_text() == "# Outside\n"
    assert "refusing to write outside" in capsys.readouterr().err


def test_file_outside_root_is_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (tmp_path / "x.md").write_text("# X\n")
    assert run_sync(str(root), "../x.md", write=True, adopt_legacy=False) == 2
    assert (tmp_path / "x.md").read_text() == "# X\n"
    assert "refusing to write outside" in capsys.readouterr().err


def test_symlink_inside_root_updates_the_resolved_file(tmp_path: Path) -> None:
    (tmp_path / "CLAUDE.md").write_text("# C\n")
    (tmp_path / "AGENTS.md").symlink_to(tmp_path / "CLAUDE.md")
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 0
    assert "<!-- tadu:rule v3 -->" in (tmp_path / "CLAUDE.md").read_text()


def test_malformed_markers_leave_the_file_untouched(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    cases = [
        "<!-- tadu:rule v1 -->\nbody\n",
        "<!-- tadu:rule v1 -->\n<!-- tadu:rule v1 -->\n<!-- /tadu:rule -->\n",
        "x\n<!-- /tadu:rule -->\n",
    ]
    for text in cases:
        (tmp_path / "AGENTS.md").write_text(text)
        assert run_sync(str(tmp_path), None, write=True, adopt_legacy=True) == 2
        assert (tmp_path / "AGENTS.md").read_text() == text
    assert "malformed tadu:rule markers; fix by hand" in capsys.readouterr().err


def test_crlf_file_changes_only_the_block(tmp_path: Path) -> None:
    old = b"# A\r\ntext\r\n<!-- tadu:rule v0 -->\r\nold\r\n<!-- /tadu:rule -->\r\nafter\r\n"
    (tmp_path / "AGENTS.md").write_bytes(old)
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 0
    written = (tmp_path / "AGENTS.md").read_bytes()
    assert written.startswith(b"# A\r\ntext\r\n<!-- tadu:rule v3 -->\r\n")
    assert written.endswith(b"<!-- /tadu:rule -->\r\nafter\r\n")
    assert b"\n" not in written.replace(b"\r\n", b"")


def test_appended_block_uses_the_files_newline(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_bytes(b"# A\r\n")
    run_sync(str(tmp_path), None, write=True, adopt_legacy=False)
    written = (tmp_path / "AGENTS.md").read_bytes()
    assert written.startswith(b"# A\r\n\r\n<!-- tadu:rule v3 -->\r\n")
    assert b"\n" not in written.replace(b"\r\n", b"")


def test_failed_write_leaves_the_original_intact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "AGENTS.md").write_bytes(b"# A\r\n")

    def refuse(_source: object, _destination: object) -> None:
        message = "disk full"
        raise OSError(message)

    monkeypatch.setattr(os, "replace", refuse)
    with pytest.raises(OSError, match="disk full"):
        run_sync(str(tmp_path), None, write=True, adopt_legacy=False)
    assert (tmp_path / "AGENTS.md").read_bytes() == b"# A\r\n"
    assert [entry.name for entry in tmp_path.iterdir()] == ["AGENTS.md"]


def test_undecodable_target_is_reported_and_not_written(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "AGENTS.md").write_bytes(b"# A \xff\n")
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 2
    assert (tmp_path / "AGENTS.md").read_bytes() == b"# A \xff\n"
    assert "could not be read: not valid UTF-8" in capsys.readouterr().err


def test_inline_and_fenced_marker_examples_get_a_real_block_appended(tmp_path: Path) -> None:
    example = "Wrap it in `<!-- tadu:rule v1 -->`.\n```md\n<!-- tadu:rule v1 -->\n```\n"
    (tmp_path / "AGENTS.md").write_text(example)
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 0
    text = (tmp_path / "AGENTS.md").read_text()
    assert text.startswith(example + "\n<!-- tadu:rule v3 -->\n")


def test_adopt_legacy_keeps_a_subsection_under_the_legacy_heading(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text(
        "## Continuous TODO, Work Log\nold\n### TODO conventions specific to this repository\nkeep\n"
    )
    run_sync(str(tmp_path), None, write=True, adopt_legacy=True)
    text = (tmp_path / "AGENTS.md").read_text()
    assert "### TODO conventions specific to this repository\nkeep\n" in text
    assert "\nold\n" not in text


def test_symlink_swapped_after_validation_cannot_redirect_the_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "real.md").write_text("# Real\n")
    outside = tmp_path / "outside.md"
    outside.write_text("# Outside\n")
    link = root / "AGENTS.md"
    link.symlink_to(root / "real.md")

    def swap_then_serve() -> str:
        link.unlink()
        link.symlink_to(outside)
        return rule_block_text()

    monkeypatch.setattr("tadu.run_sync.rule_block_text", swap_then_serve)
    assert run_sync(str(root), None, write=True, adopt_legacy=False) == 0
    assert outside.read_text() == "# Outside\n"
    assert "<!-- tadu:rule v3 -->" in (root / "real.md").read_text()


def test_block_reformatted_with_blank_lines_is_up_to_date(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    compact = rule_block_text().replace("-->\n\n", "-->\n")
    (tmp_path / "AGENTS.md").write_text("# A\n\n" + compact)
    run_sync(str(tmp_path), None, write=True, adopt_legacy=False)
    assert (tmp_path / "AGENTS.md").read_text() == "# A\n\n" + compact
    assert "up to date" in capsys.readouterr().out


def test_missing_root_is_refused(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run_sync(str(tmp_path / "absent"), None, write=True, adopt_legacy=False) == 2
    assert not (tmp_path / "absent").exists()
    assert "not a directory" in capsys.readouterr().err


def test_prettier_reflowed_block_is_up_to_date(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    reflowed = (Path(__file__).parent / "fixtures" / "rule_block_v3_prettier_100.md").read_text()
    (tmp_path / "AGENTS.md").write_text(reflowed)
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 0
    assert "up to date" in capsys.readouterr().out
    assert (tmp_path / "AGENTS.md").read_text() == reflowed


def test_changed_word_in_reflowed_block_is_drift(tmp_path: Path) -> None:
    reflowed = (Path(__file__).parent / "fixtures" / "rule_block_v3_prettier_100.md").read_text()
    (tmp_path / "AGENTS.md").write_text(reflowed.replace("searchable", "readable"))
    run_sync(str(tmp_path), None, write=True, adopt_legacy=False)
    assert (tmp_path / "AGENTS.md").read_text() == rule_block_text()


def test_backtick_info_prose_does_not_hide_existing_rule_block(tmp_path: Path) -> None:
    original = "```a`b\n\n" + rule_block_text()
    (tmp_path / "AGENTS.md").write_text(original)
    assert run_sync(str(tmp_path), None, write=True, adopt_legacy=False) == 0
    assert (tmp_path / "AGENTS.md").read_text() == original
