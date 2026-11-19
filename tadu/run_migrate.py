"""The migrate command: a tadu v1 Markdown backlog becomes a task backlog (format v2)."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.canonical_task_text import canonical_task_text
from tadu.format_1_header import format_1_header
from tadu.fresh_todo_config_text import fresh_todo_config_text
from tadu.leftover_patterns import MIGRATION_STAGING
from tadu.legacy_report import legacy_report
from tadu.migration_files import migration_files
from tadu.migration_refusal import migration_refusal
from tadu.migration_tasks import migration_tasks
from tadu.task_location import task_location
from tadu.task_problems import task_problems
from tadu.task_states import OPEN_TASK_STATES
from tadu.todo_layout import TODO_CONFIG, TODO_DIR
from tadu.unplaced_report import unplaced_report
from tadu.v1_texts import v1_texts

if TYPE_CHECKING:
    import argparse


def run_migrate(args: argparse.Namespace) -> int:
    """Print the plan; with --write, write todo/ and remove the converted files (git keeps them).

    The files are written into a staging folder, flushed to disk once and renamed to todo/, so
    thousands of tasks convert in seconds and an interrupted run leaves no half-written todo/.

    Tasks doctor would flag (a closed item without evidence, say) are still written and listed,
    so nothing is lost; fix them after migrating. Exit 2 when there is nothing to migrate.
    """
    root = Path(args.path)
    reason = migration_refusal(root)
    if reason is not None:
        print(f"tadu migrate: {root}: {reason}", file=sys.stderr)
        return 2
    tasks, categories = migration_tasks(root)
    opened = sum(1 for task in tasks if task["state"] in OPEN_TASK_STATES)
    verb = "wrote" if args.write else "would write"
    print(
        f"tadu migrate: {verb} {opened} open and {len(tasks) - opened} closed tasks, {len(categories)} categories"
    )
    print(unplaced_report(root), end="")
    print(legacy_report(root), end="")
    for task in tasks:
        problems = task_problems({k: v for k, v in task.items() if v not in (None, "", [])})
        if problems:
            print(f"  {task['id']} {task['title']!r}: {'; '.join(problems)}")
    converted = ", ".join(name for _, name in migration_files(root))
    if not args.write:
        print(f"tadu migrate: then remove {converted} (dry run: add --write)")
        return 0
    staging = root / MIGRATION_STAGING
    # writes: builds todo/ in a staging folder and renames it into place; nothing is half written
    shutil.rmtree(staging, ignore_errors=True)  # left by an interrupted run
    # writes: builds todo/ in a staging folder and renames it into place; nothing is half written
    staging.mkdir()
    # writes: builds todo/ in a staging folder and renames it into place; nothing is half written
    (staging / TODO_CONFIG).write_text(
        fresh_todo_config_text(categories, format_1_header(v1_texts(root))), encoding="utf-8"
    )
    for task in tasks:
        target = task_location(staging, task)
        # writes: builds todo/ in a staging folder and renames it into place; nothing is half written
        target.parent.mkdir(exist_ok=True)
        # writes: builds todo/ in a staging folder and renames it into place; nothing is half written
        target.write_text(canonical_task_text(task), encoding="utf-8")
    os.sync()  # one flush for all files, then todo/ appears whole or not at all
    # writes: builds todo/ in a staging folder and renames it into place; nothing is half written
    staging.replace(root / TODO_DIR)
    for file, _ in migration_files(root):
        # writes: the converted files go once todo/ is in place; git keeps their history
        file.unlink()
    print(f"tadu migrate: removed {converted}; run tadu sync --write to update the agent rules")
    return 0
