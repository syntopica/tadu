"""A repository registered in the workspace."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryEntry:
    """A repository key, its optional remote, the backlog folder inside it and its access.

    `access` is the most a tool may do to it through the workspace: read, write or admin.
    `github_id`, when the workspace gives one, is the id its GitHub remote must name.
    `proposals` is how a team board applies a change by someone who may push: a pull request
    to review (`pr`), one merged at once (`merge`) or a commit on the default branch (`direct`).
    `branch`, when set, is the branch those changes target instead of the default branch.
    """

    key: str
    remote: str | None
    backlog: str = "."
    access: str = "admin"
    github_id: int | None = None
    proposals: str = "pr"
    branch: str | None = None
