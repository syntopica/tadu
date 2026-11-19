from pathlib import Path

from git_repo import commit, git, git_repo

from tadu.backlog_item import BacklogItem
from tadu.history_event import HistoryEvent
from tadu.markdown_history import markdown_history
from tadu.markdown_items import markdown_items

ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"
LOGIN = "- [ ] Fix the login redirect.\n\n  The cookie is dropped.\n"


def current(root: Path, name: str, index: int = -1) -> BacklogItem:
    text = "\n".join((root / name).read_text().splitlines())
    return markdown_items(text, "shop", name)[index]


def summary(events: tuple[HistoryEvent, ...]) -> list[tuple[str | None, str | None, str]]:
    return [
        (
            event.commit.subject if event.commit else None,
            event.before.title if event.before else None,
            event.after.title,
        )
        for event in events
    ]


def test_follows_an_item_without_id_through_edits_and_closing(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "# TODO\n"}, "Start")
    commit(root, {"TODO.md": f"# TODO\n\n{LOGIN}"}, "Add login")
    loop = LOGIN.replace("redirect.", "redirect loop.")
    commit(root, {"TODO.md": f"# TODO\n\n{loop}"}, "Reword")
    twin = "- [ ] Fix the login redirect loop.\n\n  Also in Safari.\n"
    commit(root, {"TODO.md": f"# TODO\n\n{twin}\n{loop}"}, "Add a twin before it")
    entry = (
        "- [x] 2026-11-05 — **Backend:** Fix the login redirect loop.\n\n"
        "  The cookie is dropped.\n  - Result: Kept.\n  - Evidence: CI.\n"
    )
    commit(
        root,
        {"TODO.md": f"# TODO\n\n{twin}", "TODO_LOG.md": f"# TODO Log\n\n{entry}"},
        "Close login",
    )
    events = markdown_history(root, "", current(root, "TODO_LOG.md"), "shop")
    assert summary(events) == [
        (
            "Close login",
            "Fix the login redirect loop.",
            "**Backend:** Fix the login redirect loop.",
        ),
        ("Reword", "Fix the login redirect.", "Fix the login redirect loop."),
        ("Add login", None, "Fix the login redirect."),
    ]


def test_uncommitted_and_stops_at_creation(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "- [ ] Other.\n"}, "Other")
    commit(root, {"TODO.md": f"- [ ] Other.\n{LOGIN}"}, "Add login")
    (root / "TODO.md").write_text(f"- [ ] Other.\n{LOGIN.replace('[ ]', '[~]')}")
    events = markdown_history(root, "", current(root, "TODO.md"), "shop")
    assert [(e.commit.subject if e.commit else None, e.after.state) for e in events] == [
        (None, "~"),
        ("Add login", " "),
    ]


def test_merge_of_two_branches_that_both_changed_it(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    item = f"- [ ] Ship the export.\n\n  ID: {ID}\n\n  Priority: low\n\n  Due: 2026-12-01\n"
    commit(root, {"TODO.md": item}, "Add export")
    git(root, "checkout", "-q", "-b", "bob")
    commit(root, {"TODO.md": item.replace("low", "high")}, "Raise priority", author="Bob")
    git(root, "checkout", "-q", "main")
    commit(root, {"TODO.md": item.replace("the export", "the CSV export")}, "Name the format")
    git(root, "merge", "-q", "--no-edit", "bob", day=9)
    events = markdown_history(root, "", current(root, "TODO.md"), "shop")
    merge, *rest = events
    assert merge.commit is not None
    assert len(merge.commit.parents) == 2
    assert merge.before is not None
    assert (merge.before.fields.priority, merge.after.fields.priority) == ("low", "high")
    assert sorted(e.commit.subject for e in rest if e.commit) == [
        "Add export",
        "Name the format",
        "Raise priority",
    ]


def test_an_item_git_never_held(tmp_path: Path) -> None:
    root = git_repo(tmp_path / "shop")
    commit(root, {"TODO.md": "- [ ] Other.\n"}, "Other")
    (stale,) = markdown_items("- [ ] Never written.", "shop", "TODO.md")
    assert markdown_history(root, "", stale, "shop") == ()
