"""Say what completing a migration changes."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.completion_plan import CompletionPlan


def print_completion(plan: CompletionPlan, root: Path, source: str) -> None:
    """One line per file changed, paths relative to root; what is refused on standard error."""
    for path, _ in plan.created:
        print(f"  {path.relative_to(root)}: new, from {source}")
    for file, target, text in plan.renamed:
        done = "" if text is not None else " (already written; the old file goes)"
        print(f"  {file.path.relative_to(root)} -> {target.relative_to(root)}{done}")
    for file, _ in plan.rewritten:
        print(f"  {file.path.relative_to(root)}: gains what {source} held and it lacked")
    if plan.config:
        print(f"  {plan.config[0].relative_to(root)}: keeps the headers of {source}")
    for reason in plan.refused:
        print(f"  not done: {reason}", file=sys.stderr)
