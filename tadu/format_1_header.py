"""Keep the header of each format 1 file, which no task holds."""

from __future__ import annotations

from tadu.v1_layout import v1_layout
from tadu.v1_texts import V1_FILES


def format_1_header(texts: dict[str, str]) -> dict[str, list[str]]:
    """File name -> its lines before the first `##` heading or item, for each file that has any.

    The title, the quoted summary (a history coverage note, say) and the log marker describe
    the backlog, not one task, so the migration keeps them verbatim in todo/tadu.json.
    """
    header: dict[str, list[str]] = {}
    for name in V1_FILES:
        lines = texts.get(name, "").splitlines()
        text = [index for index in range(v1_layout(lines).header_end) if lines[index].strip()]
        if text:
            # keys: the two file names
            header[name] = lines[text[0] : text[-1] + 1]
    return header
