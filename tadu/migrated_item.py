"""Find the Markdown item a migrated task came from."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from tadu.blob_reader import ABSENT
from tadu.log_archive_years_at import log_archive_years_at
from tadu.markdown_items import markdown_items
from tadu.migration_entries import migration_entries

if TYPE_CHECKING:
    from tadu.backlog_item import BacklogItem
    from tadu.history_source import HistorySource


def migrated_item(
    source: HistorySource, commit: str, backlog: str, task_id: str
) -> BacklogItem | None:
    """The Markdown item `tadu migrate` made the task from, as it was in `commit`.

    Looked for in the backlog's TODO.md, TODO_LOG.md and archived years: the item whose `ID:`
    is the task's id, else the one whose derived id is, by running the migration again on the
    files as they were. None when the backlog had no TODO.md there.
    """
    base = PurePosixPath(backlog)
    paths = [(base / "TODO.md").as_posix(), (base / "TODO_LOG.md").as_posix()]
    paths += log_archive_years_at(source.root, commit, backlog)
    if source.blobs.object_id(source.name(commit, paths[0])) == ABSENT:
        return None
    texts = [source.blobs.read(source.name(commit, path)) for path in paths]
    for path, text in zip(paths, texts, strict=True):
        found = [
            item
            for item in (markdown_items(text, source.repository, path) if task_id in text else ())
            if item.fields.id == task_id
        ]
        if found:
            return found[0]
    names = [PurePosixPath(path).relative_to(base).as_posix() for path in paths]
    entries = migration_entries(zip(names, (text.split("\n") for text in texts), strict=True))
    for task, _, name, number in entries:
        if task["id"] == task_id:
            at = names.index(name)
            return markdown_items(texts[at], source.repository, paths[at])[number]
    return None
