"""Per-file cached values of one task folder, recomputed only for files that changed."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, cast

from tadu.cache_directory import cache_directory
from tadu.item_cache_file import item_cache_file
from tadu.item_cache_settings import RACY_NANOSECONDS
from tadu.read_item_cache import read_item_cache
from tadu.reusable_payload import reusable_payload
from tadu.scan_task_folder import scan_task_folder
from tadu.write_item_cache import write_item_cache

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path


def cached_payloads(
    folder: Path, kind: str, root: Path, build: Callable[[Path], list[object] | None]
) -> list[tuple[str, list[object]]]:
    """(file name below the folder, payload) in name order; `build` makes the payload of one file.

    Every file is stat'ed; a payload is reused only when the file's modification and change
    times, size and inode all match, so an edit, a checkout or a move is always seen. Files
    changed in the last seconds are rebuilt but not stored. A None payload skips the file.
    `kind` and `root` select the cache file, so each use keeps its own.
    """
    directory = cache_directory()
    cache_path = item_cache_file(directory, kind, root, folder) if directory else None
    old: dict[str, object] = read_item_cache(cache_path) if cache_path else {}
    trusted_before = time.time_ns() - RACY_NANOSECONDS
    scanned = scan_task_folder(folder)
    stored: dict[str, list[object]] = {}
    found: list[tuple[str, list[object]]] = []
    for name in sorted(scanned):  # a fixed order, so equal items always list the same way
        status = scanned[name]
        signature = [status.st_mtime_ns, status.st_ctime_ns, status.st_size, status.st_ino]
        entry = old.get(name)
        payload = reusable_payload(entry, signature)
        if payload is not None:
            # keys: file names relative to one backlog root, unique within it
            stored[name] = cast("list[object]", entry)
        else:
            payload = build(folder / name)
            if payload is None:
                continue
            if max(status.st_mtime_ns, status.st_ctime_ns) < trusted_before:
                # keys: file names relative to one backlog root, unique within it
                stored[name] = [signature, payload]
        found.append((name, payload))
    changed = stored.keys() != old.keys() or any(stored[n] is not old[n] for n in stored)
    if cache_path is not None and changed:
        write_item_cache(cache_path, stored)
    return found
