"""Check one tool argument against its schema property."""

from __future__ import annotations

TYPES: dict[str, type] = {"string": str, "integer": int, "boolean": bool, "array": list}


def argument_value_error(name: str, spec: dict[str, object], value: object) -> str | None:
    """Why the value does not fit the property, or None; a bool is never an integer."""
    kind = str(spec["type"])
    fits = isinstance(value, TYPES[kind]) and (kind == "boolean" or not isinstance(value, bool))
    if fits and isinstance(value, list):
        fits = all(isinstance(item, str) for item in value)
    if fits and isinstance(value, int):
        fits = value >= 0
    if not fits:
        what = "array of strings" if kind == "array" else kind
        return f"{name} must be a{'n' if kind[0] in 'ai' else ''} {what}"
    allowed = spec.get("enum")
    if isinstance(allowed, list) and value not in allowed:
        return f"{name} must be one of {', '.join(str(item) for item in allowed)}"
    return None
