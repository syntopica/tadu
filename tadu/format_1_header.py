"""Keep the header of each format 1 file, which no task holds."""

from __future__ import annotations

from tadu.v1_layout import v1_layout


def format_1_header(texts: dict[str, str]) -> dict[str, list[str]]:
    """File name -> its lines before the first `##` heading or item, for each file that has any.

    The title, the quoted summary (a history coverage note, say) and the log marker describe
    the backlog, not one task, so the migration keeps them verbatim in todo/tadu.json. The files are those of texts: the two
    Markdown files and the archived years of the log.
    """
    header: dict[str, list[str]] = {}
    for name, text in texts.items():
        lines = text.splitlines()
        shown = [index for index in range(v1_layout(lines).header_end) if lines[index].strip()]
        if shown:
            # keys: a file name appears once in texts
            header[name] = lines[shown[0] : shown[-1] + 1]
    return header
