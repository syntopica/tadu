"""Carry the format 1 fields that format 2 holds differently, or not at all."""

from __future__ import annotations

from tadu.held_field_key import held_field_key
from tadu.task_defaults import DEFAULT_TASK_TYPES, UNKNOWN_TYPE

UNHELD = ("Queue", "Estimate", "Not before", "Kind", "Check on")


def v1_field_keys(fields: dict[str, str], state: str) -> tuple[dict[str, object], list[str]]:
    """Task keys for Labels, Queue, Estimate, Not before, Kind and Check on, and the lines left.

    The first label that is a default type is the type, the others stay labels. What
    held_field_key gives no key keeps its field line, in file order, for the task's notes: a
    value that does not parse and `Queue: ready` on an item that is not pending.
    `Queue: backlog` is the default and needs nothing.
    """
    labels = [label.strip() for label in fields.get("Labels", "").split(",") if label.strip()]
    label_type = next((label for label in labels if label in DEFAULT_TASK_TYPES), UNKNOWN_TYPE)
    keys: dict[str, object] = {
        "type": label_type,
        "labels": [label for label in labels if label != label_type],
    }
    kept: list[str] = []
    for name, value in fields.items():
        if name not in UNHELD or (name, value) == ("Queue", "backlog"):
            continue
        key = held_field_key(name, value, state)
        if key is None:
            kept.append(f"{name}: {value}")
        else:
            # keys: each field name is read once, and each maps to its own key
            keys[key] = int(value) if key == "estimate" else value
    return keys, kept
