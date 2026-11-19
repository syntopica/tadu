"""Whether a repository GitHub described may be read by the asking user."""

from __future__ import annotations


def can_pull(repository: object) -> bool:
    """False for anything but a JSON object, or one whose `permissions` withhold `pull`.

    An object without `permissions` (GitHub leaves them out for some tokens) can be read:
    GitHub only describes a repository to someone who can see it.
    """
    if not isinstance(repository, dict):
        return False
    permissions = repository.get("permissions")
    return not isinstance(permissions, dict) or bool(permissions.get("pull"))
