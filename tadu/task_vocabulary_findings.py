"""Findings about a valid task's values against the backlog's declarations and the date."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tadu.config_names import config_names
from tadu.finding import Finding
from tadu.task_defaults import DEFAULT_TASK_TYPES, STALE_AFTER_DAYS, UNKNOWN_CATEGORY, UNKNOWN_TYPE
from tadu.task_key_order import TASK_KEY_ORDER
from tadu.task_states import OPEN_TASK_STATES
from tadu.task_str import task_str

if TYPE_CHECKING:
    from tadu.task_file import TaskFile


def task_vocabulary_findings(
    file: TaskFile, config: dict[str, object], today: date
) -> tuple[Finding, ...]:
    """Undeclared category, type or milestone, triage left to do, stale work, unknown keys."""
    task, path = file.task, str(file.path)
    types = config_names(config, "types") or frozenset(DEFAULT_TASK_TYPES)
    declared = {
        "category": config_names(config, "categories") | {UNKNOWN_CATEGORY},
        "type": types | {UNKNOWN_TYPE},
        "milestone": config_names(config, "milestones"),
    }
    codes = {"category": "J008", "type": "J009", "milestone": "J019"}
    findings = [
        Finding(codes[key], "warning", path, 0, f"{key} {value!r} is not declared in tadu.json")
        for key, names in declared.items()
        if (value := task_str(task, key)) is not None and value not in names
    ]
    state = task_str(task, "state")
    unknown = {"priority": "untriaged", "category": UNKNOWN_CATEGORY, "type": UNKNOWN_TYPE}
    gaps = [f"{key} {value}" for key, value in unknown.items() if task.get(key) == value]
    if state in OPEN_TASK_STATES and gaps:
        findings.append(Finding("J010", "warning", path, 0, f"needs triage: {', '.join(gaps)}"))
    started = task_str(task, "started")
    limit = config.get("stale_after_days", STALE_AFTER_DAYS)
    if state == "in_progress" and started and isinstance(limit, int):
        days = (today - date.fromisoformat(started)).days
        if days > limit:
            message = (
                f"in progress for {days} days (started {started}): finish, hand over or block it"
            )
            findings.append(Finding("J018", "warning", path, 0, message))
    unknown_keys = [k for k in task if k not in TASK_KEY_ORDER and not k.startswith("x-")]
    if unknown_keys:
        message = f"unknown key(s) {', '.join(unknown_keys)}; kept, but check for a typo"
        findings.append(Finding("J011", "warning", path, 0, message))
    return tuple(findings)
