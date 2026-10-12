"""Resolve and read the file sync would rewrite, refusing unsafe targets."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.has_malformed_rule_markers import has_malformed_rule_markers
from tadu.read_text_exact import read_text_exact
from tadu.resolve_inside_root import resolve_inside_root
from tadu.unreadable_file_error import UnreadableFileError

if TYPE_CHECKING:
    from pathlib import Path


def read_sync_source(candidate: Path, root: Path) -> tuple[Path, str] | None:
    """The resolved target and its text, or None after reporting why sync must refuse."""
    target = resolve_inside_root(candidate, root)
    if target is None:
        print(f"{candidate}: refusing to write outside {root}", file=sys.stderr)
        return None
    try:
        before = read_text_exact(target) if target.is_file() else ""
    except UnreadableFileError as error:
        print(f"{candidate} could not be read: {error.reason}", file=sys.stderr)
        return None
    if has_malformed_rule_markers(before):
        print(f"{candidate}: malformed tadu:rule markers; fix by hand", file=sys.stderr)
        return None
    return target, before
