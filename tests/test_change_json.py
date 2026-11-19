from pathlib import Path
from typing import TYPE_CHECKING, cast

from tadu.change_json import change_json
from tadu.change_source import ChangeSource
from tadu.git_commit import GitCommit
from tadu.markdown_items import markdown_items

if TYPE_CHECKING:
    from tadu.blob_reader import BlobReader

ONE = GitCommit("a" * 40, "a" * 10, ("b" * 40,), "2026-11-01T09:00:00+00:00", "Ana", "S", ())
SOURCE = ChangeSource("shop", "store", Path("/r"), "", ".", cast("BlobReader", None))
ID = "t-3f2a1b4c-5d6e-4f70-8a91-b2c3d4e5f607"


def test_created_changed_and_removed_entries() -> None:
    (old,) = markdown_items(f"- [ ] Ship.\n\n  ID: {ID}", "shop", "TODO.md")
    (new,) = markdown_items(f"- [~] Ship it.\n\n  ID: {ID}", "shop", "TODO.md")
    created = change_json(SOURCE, ONE, (None, new), "created")
    assert (created["created"], created["key"], created["title"], created["event"]) == (
        True,
        ID,
        "Ship it.",
        "created",
    )
    assert (created["repository"], created["project"], created["author"]) == (
        "shop",
        "store",
        "Ana",
    )
    changed = change_json(SOURCE, ONE, (old, new), "started")
    assert [c["field"] for c in changed["changes"]] == ["state", "title"]
    removed = change_json(SOURCE, ONE, (old, None), "removed")
    assert removed["changes"] == [{"field": "file", "before": "TODO.md", "after": None}]
    assert (
        removed["created"],
        removed["lines"],
        removed["before_text"],
        removed["after_text"],
    ) == (
        False,
        [],
        old.text,
        "",
    )
    assert (removed["title"], removed["path"]) == ("Ship.", "TODO.md")
