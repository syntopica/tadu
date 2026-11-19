"""File names of the workspace configuration, and of the GitHub ids a board learns.

The shared file, the untracked per-machine file, and what a board that signs in with
GitHub writes down beside them: the repositories' GitHub ids and the sessions.
"""

from __future__ import annotations

WORKSPACE_FILE = "tadu-workspace.toml"
LOCAL_FILE = "tadu-workspace.local.toml"
GITHUB_IDS_FILE = "tadu-workspace.github-ids.json"
SESSIONS_FILE = "tadu-workspace.sessions.json"
