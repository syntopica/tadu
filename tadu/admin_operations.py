"""The operations that set up or rewrite a whole backlog."""

from __future__ import annotations

from tadu.operation import Operation
from tadu.param import Param

FILE = Param("file", "text", "instruction file (default: AGENTS.md, else CLAUDE.md)")

ADMIN_OPERATIONS = (
    Operation(
        "sync",
        "write the marked rule block into the instruction file",
        (FILE, Param("adopt_legacy", "flag", "replace an unmarked legacy rule section")),
        access="admin",
    ),
    Operation(
        "init",
        "start a tadu backlog in a repository without one",
        (
            FILE,
            Param(
                "format",
                "choice",
                "1: TODO.md and TODO_LOG.md (default); 2: a task backlog, one JSON file per task",
                ("1", "2"),
                default="1",
            ),
        ),
        access="admin",
    ),
    Operation(
        "archive",
        "move old closed tasks to todo/archive/ as todo/tadu.json's policy says (format 2)",
        (),
        access="admin",
    ),
    Operation(
        "fmt", "rewrite task files that are not in canonical form (format 2)", (), access="admin"
    ),
    Operation(
        "migrate",
        "turn a TODO.md / TODO_LOG.md backlog into a task backlog (format 2)",
        (
            Param(
                "recover",
                "flag",
                "bring into a migrated backlog what an older migrate lost (IDs, fields, text), "
                "read from git",
            ),
            Param(
                "revision",
                "text",
                "with --recover: the commit that still has TODO.md / TODO_LOG.md "
                "(default: the one before the commit that deleted them)",
                flags=("--from",),
                metavar="REV",
            ),
        ),
        access="admin",
    ),
)
