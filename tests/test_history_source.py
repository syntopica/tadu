from pathlib import Path
from typing import TYPE_CHECKING, cast

from history_repo import history_source

from tadu.history_source import HistorySource

if TYPE_CHECKING:
    from tadu.blob_reader import BlobReader


def test_pathspec_and_name(tmp_path: Path) -> None:
    source = history_source(tmp_path, cast("BlobReader", None), "app/")
    assert HistorySource.pathspec("TODO.md") == ":(literal)TODO.md"
    assert source.name("abc", "TODO_LOG.md") == "abc:app/TODO_LOG.md"
