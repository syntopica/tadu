"""JSON-ready form of a resolved dependency."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.open_states import OPEN_STATES

if TYPE_CHECKING:
    from tadu.dependency import Dependency


def dependency_json(dependency: Dependency) -> dict[str, object]:
    """The dependency; `open` is null when the target was not found."""
    state = dependency.state
    return {
        "id": dependency.id,
        "repository": dependency.repository,
        "state": state,
        "column": dependency.column,
        "open": None if state is None else state in OPEN_STATES,
    }
