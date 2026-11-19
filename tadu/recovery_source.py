"""Find the commit a recovery reads the Markdown backlog from, and read it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.git_output import git_output
from tadu.migration_revision import migration_revision
from tadu.v1_texts import V1_FILES

if TYPE_CHECKING:
    from pathlib import Path


def recovery_source(root: Path, revision: str | None) -> tuple[str, dict[str, str]] | str:
    """(full commit id, TODO.md and TODO_LOG.md as it has them), or why there is none.

    `revision` defaults to the first of migration_revision's that has either file. The id is
    resolved, so two names of one commit are one recovery.
    """
    candidates = (revision,) if revision else migration_revision(root)
    for rev in candidates:
        found = git_output(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
        commit = (found or b"").decode().strip()
        # keys: the two Markdown file names
        raw = {
            name: git_output(root, "show", f"{commit}:./{name}") if commit else None
            for name in V1_FILES
        }
        try:
            # keys: the two Markdown file names
            texts = {name: data.decode() for name, data in raw.items() if data is not None}
        except UnicodeDecodeError:
            return f"{rev}: TODO.md or TODO_LOG.md is not UTF-8 text; convert it, then give --from"
        if texts:
            return commit, texts
    where = (
        f"{candidates[-1]} has no TODO.md or TODO_LOG.md"
        if candidates
        else "no commit deleted TODO.md"
    )
    return f"{where}; give --from REV, a commit that has them"
