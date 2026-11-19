"""Read one `git log --raw` file line."""

from __future__ import annotations

from tadu.git_file_change import GitFileChange


def raw_file_change(raw: str, path: str) -> GitFileChange:
    """The change a raw line describes: `:` and two modes, two blobs, a status for one parent.

    A merge (`-c`) starts with one colon per parent and lists a mode and a blob per parent, then
    the result's.
    """
    parents = len(raw) - len(raw.lstrip(":"))
    blobs = raw.lstrip(":").split()[parents + 1 : 2 * parents + 2]
    return GitFileChange(path, tuple(blobs[:-1]), blobs[-1])
