"""Write the changes that complete a migration, then remove the format 1 files."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tadu.write_completion import write_completion

if TYPE_CHECKING:
    from pathlib import Path

    from tadu.completion_plan import CompletionPlan


def apply_completion(plan: CompletionPlan, removed: tuple[Path, ...]) -> bool:
    """Write the plan (write_completion); False after reporting what stopped it."""
    try:
        return write_completion(plan, removed)
    except OSError as error:
        print(f"tadu migrate: {error}; run it again to finish", file=sys.stderr)
        return False
