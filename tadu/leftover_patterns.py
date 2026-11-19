"""The names of what a tadu write that stopped halfway leaves behind."""

from __future__ import annotations

import re

# tempfile.mkstemp names: "." + target name + "." + 8 of [a-z0-9_] + ".tmp"
ROOT_TEMPORARY = re.compile(r"\.(?:TODO\.md|TODO_LOG\.md|AGENTS\.md|CLAUDE\.md)\.[a-z0-9_]{8}\.tmp")
TASK_TEMPORARY = re.compile(r"\..+\.json\.[a-z0-9_]{8}\.tmp")
REPOSITORY_TEMPORARY = re.compile(f"{ROOT_TEMPORARY.pattern}|{TASK_TEMPORARY.pattern}")
# write_item_cache names: the cache file name + "." + process id + ".tmp"
CACHE_TEMPORARY = re.compile(r"(?:items|checks)-[0-9a-f]{24}\.json\.\d+\.tmp")
MIGRATION_STAGING = ".todo.migrating"
# A temporary file lives for the milliseconds of one write; one this old was left by a write
# that was killed, and is removed by the next write to its folder.
STALE_SECONDS = 60
