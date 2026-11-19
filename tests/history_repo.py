from pathlib import Path

from tadu.blob_reader import BlobReader
from tadu.history_source import HistorySource


def history_source(root: Path, blobs: BlobReader, prefix: str = "") -> HistorySource:
    """The history source of the Markdown backlog at root."""
    return HistorySource(root, prefix, ("TODO.md", "TODO_LOG.md"), "shop", blobs)
