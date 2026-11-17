"""Write examples/todo/ from tadu's own backlog items, through the canonical writer."""

import json
import shutil
from pathlib import Path

from v2 import canonical, location

ROOT = Path(__file__).parent / "examples" / "todo"
MUTATION = "t-3f2a9c1e-7b4d-4e8a-9c21-5d6e7f8a9b0c"
MCP = "t-8c41d2e7-0a6b-4f3c-b5d8-2e9f1a7c6b43"
BOARD_RIGHTS = "t-b7e3a915-4c2d-4a8f-8e61-0f9d3c2b1a57"
FEED = "t-5a9e0c3b-2d71-4b6e-9f84-7c1a2e3d4f56"
UNION = "t-e1c7b2a4-9f3d-4c58-a6b0-8d2f7e9c1a34"
HISTORY = "t-4d6f8a2c-1e3b-4c5d-8e7f-9a0b1c2d3e4f"
DUPLICATE = "t-9b2e4d6f-8a1c-4e3b-a5d7-6c8e0f2a4b19"

CONFIG = {
    "tadu": 2,
    "categories": {"board": "Board", "cli": "CLI", "format": "Format", "adoption": "Adoption",
                   "release": "Release", "ci": "CI", "docs": "Docs"},
    "types": ["bug", "feature", "chore", "test", "docs", "refactor", "perf", "security", "decision"],
    "milestones": {"v0-2": {"name": "0.2", "due": "2026-12-15"}},
    "stale_after_days": 14,
    "archive": {"after_days": 30},
}

TASKS = [
    ({  # blocked only by another task: closing that task unblocks it
        "tadu": 2, "id": MCP, "title": "Add an MCP adapter as an optional extra",
        "state": "blocked", "category": "board", "type": "feature", "priority": "normal",
        "labels": ["mcp", "agents"], "milestone": "v0-2", "created": "2026-11-04", "created_by": "ana",
        "assignees": ["ana"], "estimate": 240, "blocked_by": [MUTATION], "related": [BOARD_RIGHTS],
        "notes": ["Core keeps no dependencies, so the adapter ships as an extra.",
                  "",
                  "Smallest next step: expose list and show as read-only tools in an mcp extra."],
        "links": ["https://modelcontextprotocol.io/specification"],
        "done_when": ["`pip install tadu[mcp]` serves list and show, read-only",
                      "`uv run pytest` passes with and without the extra"],
    }, False),
    ({  # in progress, with a deadline
        "tadu": 2, "id": MUTATION,
        "title": "Add one shared mutation function with lock, hash check, commit and push",
        "state": "in_progress", "category": "board", "type": "refactor", "priority": "high",
        "milestone": "v0-2", "created": "2026-11-04", "started": "2026-11-10", "due": "2026-11-27",
        "assignees": ["ana", "agent:claude"],
        "notes": ["Used by the CLI, the board and MCP, with a recoverable journal for close, which writes two files.",
                  "",
                  "Smallest next step:",
                  "",
                  "- extract the lock and changed-since-read check of tadu close into a function",
                  "- make it take an item ID and the file hash the caller last saw"],
    }, False),
    ({  # quick capture: priority not decided yet
        "tadu": 2, "id": HISTORY, "title": "Show item history from git log",
        "state": "pending", "category": "board", "type": "feature", "priority": "untriaged",
        "created": "2026-11-15", "created_by": "agent:claude", "defer_until": "2026-12-01",
        "discovered_from": MUTATION,
        "notes": ["Smallest next step: print the commits that touched an item's file, for one key:",
                  "",
                  "```sh",
                  "git log --follow --format='%h %ad %s' --date=short -- todo/open/<id>.json",
                  "```"],
    }, False),
    ({  # blocked by an external condition: the blocker and the smallest unblock action are fields
        "tadu": 2, "id": BOARD_RIGHTS,
        "title": "Decide who opens a company workspace's board and whether they only view or also move and edit cards",
        "state": "blocked", "category": "board", "type": "decision", "priority": "high",
        "created": "2026-11-04",
        "blocker": "The owner's decision: local-only versus a shared server with auth, and the write path for people who do not use agents.",
        "unblock": "The owner states, for the first company workspace, who uses the board and with what rights.",
        "notes": ["The read-only first version in docs/superpowers/specs/2026-11-04-tadu-board-design.md does not depend on it."],
    }, False),
    ({  # done, recently: stays in closed/
        "tadu": 2, "id": FEED, "title": "Add a recently-done feed from the logs",
        "state": "done", "category": "board", "type": "feature", "priority": "normal",
        "created": "2026-11-05", "notes": ["Agents and people want what was finished lately without reading the log."],
        "closed": "2026-11-10", "result": "tadu feed prints the done and cancelled log entries of the last 14 days, newest first, as JSON lines.",
        "evidence": ["tests/test_run_feed.py passes", "uv run codeality-py gate: all passed, 100% coverage"],
        "files": ["tadu/run_feed.py", "tadu/recently_done.py"],
        "x-jira": "TADU-41",
    }, False),
    ({  # closed as a duplicate: the duplicate check found the twin after it was recorded
        "tadu": 2, "id": DUPLICATE, "title": "Expose tadu list to agents over MCP",
        "state": "cancelled", "category": "board", "type": "feature", "priority": "normal",
        "created": "2026-11-12", "created_by": "agent:codex",
        "closed": "2026-11-12", "resolution": f"Duplicate of {MCP}.", "duplicate_of": MCP,
    }, False),
    ({  # cancelled more than 30 days ago: moved whole to archive/2026/ (a small year: no month folders)
        "tadu": 2, "id": UNION, "title": "Recommend TODO_LOG.md merge=union",
        "state": "cancelled", "category": "adoption", "type": "decision", "priority": "normal",
        "closed": "2026-10-12",
        "resolution": "Rejected: a union merge can interleave the lines of two multi-line entries and attach one entry's Evidence to the other; the README says to resolve log conflicts by hand and run tadu doctor.",
    }, True),
]

if __name__ == "__main__":
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True)
    (ROOT / "tadu.json").write_text(json.dumps(CONFIG, indent=2) + "\n")
    for task, archived in TASKS:
        p = location(ROOT, task, archived)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(canonical(task))
    print("\n".join(str(p.relative_to(ROOT.parent)) for p in sorted(ROOT.rglob("*.json"))))
