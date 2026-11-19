def sample_task(number: int, state: str = "pending", **overrides: object) -> dict[str, object]:
    """A valid task with a predictable id (t-0000000n-...); closing keys are filled in for closed states."""
    task: dict[str, object] = {
        "tadu": 2,
        "id": f"t-{number:08x}-0000-4000-8000-{number:012x}",
        "title": f"Task {number}",
        "state": state,
        "category": "core",
        "type": "feature",
        "priority": "normal",
    }
    if state == "done":
        task.update(closed="2026-11-01", result="Done.", evidence=["pytest passes"])
    if state == "cancelled":
        task.update(closed="2026-11-01", resolution="Dropped.")
    task.update(overrides)
    return task


def sample_id(number: int) -> str:
    """The id sample_task gives task `number`."""
    return str(sample_task(number)["id"])
