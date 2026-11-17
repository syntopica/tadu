"""Find cycles in blocked_by relations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.task_strings import task_strings

if TYPE_CHECKING:
    from tadu.task_file import TaskFile


def blocked_by_cycles(by_id: dict[str, TaskFile]) -> tuple[tuple[str, ...], ...]:
    """One cycle per task that starts one, as the ids along it ending where it started (A, B, A).

    Tasks are taken in order; a cycle is reported from its first task only, and each search
    visits a task once, so the cost stays linear in the tasks reachable from the start.
    """
    cycles: list[tuple[str, ...]] = []
    done: set[str] = set()
    for start in by_id:
        stack: list[tuple[str, list[str]]] = [(start, [start])]
        seen = {start}
        while stack:
            current, trail = stack.pop()
            for target in task_strings(by_id[current].task, "blocked_by"):
                if target == start and len(trail) > 1 and not done.intersection(trail):
                    cycles.append((*trail, start))
                    stack.clear()
                    break
                if target in by_id and target not in seen and target not in done:
                    seen.add(target)
                    stack.append((target, [*trail, target]))
        done.add(start)
    return tuple(cycles)
