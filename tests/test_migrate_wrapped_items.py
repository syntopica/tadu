from pathlib import Path

from tadu.is_category_prefix import is_category_prefix
from tadu.migration_tasks import migration_tasks
from tadu.task_problems import task_problems

TODO = """# TODO

## Mailbox and chat pass

- [ ] **Coverage database hardening (final review minors):** wire the saved views
  and a second line about the thing with the
third line that is not indented.

  Context paragraph.
- [ ] **CI portability:** short thing
- [ ] **Needs proof (open):** an open item
  - Evidence: ran the suite
"""


def test_a_long_bold_lead_is_the_title_and_the_section_is_the_category(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(TODO)
    tasks, _ = migration_tasks(tmp_path)
    lead, short, proof = tasks
    assert lead["title"] == "Coverage database hardening (final review minors)"
    assert lead["category"] == "mailbox-and-chat-pass"
    assert lead["notes"] == [
        "wire the saved views and a second line about the thing with the third line that is not indented.",
        "",
        "Context paragraph.",
    ]
    assert (short["title"], short["category"]) == ("short thing", "ci-portability")
    assert proof["notes"] == ["an open item", "", "Evidence: ran the suite"]
    for task in tasks:
        assert task_problems({k: v for k, v in task.items() if v not in (None, "", [])}) == ()


def test_only_a_short_plain_label_is_a_category() -> None:
    assert is_category_prefix("CI portability")
    assert not is_category_prefix("Coverage database hardening (final review minors)")
    assert not is_category_prefix("one two three four")


def test_section_prose_goes_to_the_notes_of_the_first_item(tmp_path: Path) -> None:
    (tmp_path / "TODO.md").write_text(
        "# TODO\n\nIntro before any section.\n\n## Release\n\nShip it in order.\nCheck the tag.\n\n"
        "- [ ] First\n  - Evidence: seen\n- [ ] Second\n  Plain note.\n"
    )
    first, second = migration_tasks(tmp_path)[0]
    assert first["notes"] == ["Ship it in order.", "Check the tag.", "", "Evidence: seen"]
    assert second["notes"] == ["Plain note."]
