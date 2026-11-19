"""The repositories `tadu changes` reads."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.change_repository import ChangeRepository
from tadu.root_labels import root_labels
from tadu.scan_problem import ScanProblem
from tadu.scope_root import scope_root
from tadu.scope_workspace import scope_workspace

if TYPE_CHECKING:
    from tadu.scope import Scope


def change_repositories(
    scope: Scope,
) -> tuple[tuple[ChangeRepository, ...], tuple[ScanProblem, ...]]:
    """The repositories of the roots given (default `.`), else those of the workspace.

    Only `scope.repository` when given. Roots are labelled as `tadu list` labels them. A
    workspace repository without a checkout path on this machine is a problem, not a
    repository. WorkspaceError when the workspace does not load, when both are given, or when
    the repository is not in the scope.
    """
    if scope.workspace is None:
        wanted = scope_root(scope)[0] if scope.repository is not None else None
        labels = root_labels(scope.paths or (".",))
        return tuple(
            ChangeRepository(label, None, root)
            for label, root in labels.items()
            if wanted in (None, label)
        ), ()
    loaded, local = scope_workspace(scope)
    found: list[ChangeRepository] = []
    problems: list[ScanProblem] = []
    for entry in loaded.repositories:
        project = next((p.key for p in loaded.projects if entry.key in p.repositories), None)
        root = local.paths.get(entry.key)
        if root is None:
            problems.append(ScanProblem(entry.key, "no checkout path in tadu-workspace.local.toml"))
        else:
            found.append(ChangeRepository(entry.key, project, root, entry.backlog))
    return tuple(found), tuple(problems)
