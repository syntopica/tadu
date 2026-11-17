"""Name repository roots given as paths, never two alike."""

from __future__ import annotations

from collections import Counter
from pathlib import Path


def root_labels(texts: tuple[str, ...]) -> dict[str, Path]:
    """Label to resolved root, in the order given, each root once.

    A root is labelled by its directory name when no other root shares it, else by
    its full resolved path, so two checkouts both named `api` stay apart.
    """
    # keys: drops the same directory given twice, on purpose.
    roots = list(dict.fromkeys(Path(text).resolve() for text in texts))
    # path-name: counted to find the names more than one root has.
    names = Counter(root.name for root in roots)
    # path-name: a label only when no other root has it, else the full path stands in.
    # keys: a name has no `/` and a full path has, and each root appears once.
    return {(root.name if names[root.name] == 1 else str(root)): root for root in roots}
