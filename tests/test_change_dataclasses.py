from pathlib import Path
from typing import TYPE_CHECKING, cast

from tadu.change_entry import ChangeEntry
from tadu.change_repository import ChangeRepository
from tadu.change_source import ChangeSource
from tadu.history_entry import HistoryEntry

if TYPE_CHECKING:
    from tadu.blob_reader import BlobReader


def test_values_are_kept() -> None:
    repository = ChangeRepository("shop", None, Path("/r"))
    assert (repository.backlog, repository.project) == (".", None)
    source = ChangeSource("shop", "store", Path("/r"), "app/", "docs", cast("BlobReader", None))
    assert (source.prefix, source.backlog, source.project) == ("app/", "docs", "store")


def test_a_change_entry_is_a_history_entry_with_its_item() -> None:
    extra = set(ChangeEntry.__annotations__) - set(HistoryEntry.__annotations__)
    assert extra == {"repository", "project", "key", "title", "event"}
    assert set(HistoryEntry.__annotations__) <= set(ChangeEntry.__annotations__)
