"""tadu task format v2 (draft proposal): canonical writer, versioned reader, checker, lifecycle.

    python v2.py check DIR [--today D]
    python v2.py ready DIR [--today D]            open tasks nothing blocks or defers, by priority
    python v2.py show DIR ID                      a task with its computed reverse relations
    python v2.py add DIR --title T --category C --type Y [--priority P] [options] [--write]
    python v2.py set DIR ID key=value|key+=value|key-=value|key= ... [--write]
    python v2.py claim DIR ID --as WHO [--force] [--write]
    python v2.py close DIR ID (--evidence E [--result R] | --resolution X | --duplicate-of ID) [--write]
    python v2.py archive DIR [--today D] [--write]

DIR is a repository root holding todo/, or todo/ itself. Every write command is a dry run
unless --write is given, like tadu sync and tadu close. Every write is validated first.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import date, timedelta
from pathlib import Path

CURRENT = 2
OPEN_STATES = ("pending", "in_progress", "blocked")
DEFAULT_TYPES = ["bug", "feature", "chore", "test", "docs", "refactor", "perf", "security"]
PRIORITY_RANK = {"urgent": 0, "high": 1, "untriaged": 2, "normal": 3, "low": 4}
MONTH_FOLDERS_MIN = 10  # split an archive year into months only at >= 10 tasks per month on average
STALE_AFTER_DAYS = 14  # in progress longer than this (from started) is reported
UNKNOWN_CATEGORY = "general"  # always allowed: tadu's fallback category, used when nobody has decided
UNKNOWN_TYPE = "untriaged"  # always allowed: type not decided yet

# Canonical key order: identity, classification, planning, relations, description, then the
# closing block last, so closing a task only appends lines (REPORT 8.1, 9.1).
ORDER = [
    "tadu",
    "id",
    "title",
    "state",
    "category",
    "type",
    "priority",
    "labels",
    "milestone",
    "created",
    "created_by",
    "started",
    "due",
    "defer_until",
    "queue",
    "assignees",
    "estimate",
    "parent",
    "blocked_by",
    "related",
    "discovered_from",
    "blocker",
    "unblock",
    "notes",
    "done_when",
    "links",
    "closed",
    "result",
    "evidence",
    "resolution",
    "superseded_by",
    "duplicate_of",
    "files",
]
LIST_KEYS = {"labels", "assignees", "blocked_by", "related", "notes", "done_when", "links", "evidence", "files"}
ID_KEYS = ("parent", "discovered_from", "superseded_by", "duplicate_of")
ID_LIST_KEYS = ("blocked_by", "related")

HERE = Path(__file__).parent
LINE_FIELDS = ("notes", "done_when", "evidence")  # Markdown stored as an array of lines

# High-confidence secret formats. Task files are committed and read by agents, so a pasted key
# spreads. Findings name the kind and the line, never the value (doctor output lands in logs).
SECRETS = [
    (
        "a private key block",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY( BLOCK)?-----"),
    ),
    ("an AWS access key id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("a GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("a Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("an OpenAI or Anthropic API key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}")),
    ("a Stripe secret key", re.compile(r"\b[rs]k_(?:live|test)_[A-Za-z0-9]{16,}")),
    ("a Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("a JSON web token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    (
        "a credential assignment",
        re.compile(
            r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[:=]\s*['\"]?"
            r"(?=[A-Za-z0-9/+_=-]*\d)[A-Za-z0-9/+_=-]{16,}"
        ),
    ),
]


def secret_findings(text: str) -> list[tuple[int, str]]:
    """(line number, kind) for every secret-looking match in a file."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        for kind, pattern in SECRETS:
            if pattern.search(line):
                out.append((n, kind))
                break
    return out


def lines_text(task: dict, key: str) -> str:
    """A line field read back as Markdown."""
    return "\n".join(task.get(key, []))


def today_of(a: argparse.Namespace | None = None) -> str:
    return (getattr(a, "today", None) if a else None) or os.environ.get("TADU_TODAY") or date.today().isoformat()


# ------------------------------------------------------------------ writing


def trim_lines(value: list) -> list:
    """Drop blank lines at the start and the end; blank lines inside are content."""
    start, end = 0, len(value)
    while start < end and value[start] == "":
        start += 1
    while end > start and value[end - 1] == "":
        end -= 1
    return value[start:end]


def canonical(task: dict) -> str:
    """The one accepted text of a task: known keys in ORDER, unknown keys after them, x- keys last."""
    task = {
        k: (trim_lines(v) if k in LINE_FIELDS and isinstance(v, list) and all(isinstance(x, str) for x in v) else v)
        for k, v in task.items()
    }
    known = [k for k in ORDER if k in task]
    unknown = [k for k in task if k not in ORDER and not k.startswith("x-")]
    ext = sorted(k for k in task if k.startswith("x-"))
    ordered = {k: task[k] for k in known + unknown + ext if task[k] not in (None, "", [], {})}
    return json.dumps(ordered, indent=2, ensure_ascii=False) + "\n"


def write(path: Path, task: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(canonical(task), encoding="utf-8")
    os.replace(tmp, path)


def location(root: Path, task: dict, archived: bool = False, by_month: bool = False) -> Path:
    """open/ while open, closed/ once closed, archive/YYYY/ (or YYYY/MM/) when archived."""
    if task["state"] in OPEN_STATES:
        return root / "open" / f"{task['id']}.json"
    if archived:
        y, m = task["closed"][:4], task["closed"][5:7]
        return root / "archive" / y / (m if by_month else "") / f"{task['id']}.json"
    return root / "closed" / f"{task['id']}.json"


# ------------------------------------------------------------------ reading

# One function per version step. v1 is Markdown, converted by migrate_v1.py, so the chain
# starts at 2; a future v3 adds UPGRADES[2] = lambda t: {**t, "tadu": 3, ...}.
UPGRADES: dict[int, object] = {}


def read_task(path: Path) -> tuple[dict, bool]:
    """The task upgraded to CURRENT, and whether this tool may write it back."""
    task = json.loads(path.read_text(encoding="utf-8"))
    version = task.get("tadu")
    if not isinstance(version, int):
        raise ValueError("no integer tadu version")
    if version > CURRENT:
        return task, False
    while version < CURRENT:
        task = UPGRADES[version](task)  # type: ignore[operator]
        version = task["tadu"]
    return task, True


def todo_root(d: Path) -> Path:
    return d / "todo" if (d / "todo").is_dir() else d


def config(root: Path) -> dict:
    p = root / "tadu.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def load(root: Path) -> dict[str, tuple[Path, dict]]:
    """Every readable task by id, from open/, closed/ and archive/."""
    tasks = {}
    for path in sorted(p for sub in ("open", "closed", "archive") for p in (root / sub).rglob("*.json")):
        try:
            task, _ = read_task(path)
            tasks.setdefault(task["id"], (path, task))
        except (ValueError, KeyError):
            continue
    return tasks


def resolve(tasks: dict, key: str) -> str:
    """A full id from an id or a unique prefix; never a guess."""
    if key in tasks:
        return key
    hits = [i for i in tasks if i.startswith(key)] if len(key) >= 10 else []
    if len(hits) == 1:
        return hits[0]
    raise SystemExit(f"{key}: {'ambiguous: ' + ', '.join(hits) if hits else 'no such task'}")


def short(tasks: dict, iid: str) -> str:
    """Shortest unique prefix, at least 8 hex digits after t-, as git shows commits."""
    n = 10
    while n < len(iid) and any(o != iid and o.startswith(iid[:n]) for o in tasks):
        n += 1
    return iid[:n]


def waiting_on(tasks: dict, task: dict) -> list[str]:
    """blocked_by targets that are still open (or unknown)."""
    return [b for b in task.get("blocked_by", []) if b not in tasks or tasks[b][1]["state"] in OPEN_STATES]


def references(task: dict) -> list[tuple[str, str]]:
    """(field, id) for every relation the task stores."""
    refs = [(k, task[k]) for k in ID_KEYS if task.get(k)]
    refs += [(k, x) for k in ID_LIST_KEYS for x in task.get(k, [])]
    return refs


def schema_errors(task: dict) -> list[str]:
    import jsonschema

    v = jsonschema.Draft202012Validator(json.loads((HERE / "task.v2.schema.json").read_text()))
    return [f"{'/'.join(map(str, e.path)) or '(task)'}: {e.message}" for e in v.iter_errors(task)]


# ------------------------------------------------------------------ checking


def check(d: Path, today: str | None = None) -> list[tuple[str, str, str, str]]:
    """Findings (path, severity, code, message), like tadu doctor."""
    import jsonschema

    today = today or today_of()
    root = todo_root(d)
    task_schema = jsonschema.Draft202012Validator(json.loads((HERE / "task.v2.schema.json").read_text()))
    cfg_schema = jsonschema.Draft202012Validator(json.loads((HERE / "config.v2.schema.json").read_text()))
    out: list[tuple[str, str, str, str]] = []
    rel = lambda p: str(p.relative_to(root.parent))  # noqa: E731

    cfg: dict = {}
    cfg_path = root / "tadu.json"
    if not cfg_path.is_file():
        out.append((rel(cfg_path), "error", "C001", "todo/tadu.json is missing"))
    else:
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            for e in cfg_schema.iter_errors(cfg):
                out.append((rel(cfg_path), "error", "C002", e.message))
        except ValueError as e:
            out.append((rel(cfg_path), "error", "C002", f"not JSON: {e}"))
    categories = set(cfg.get("categories", {})) | {UNKNOWN_CATEGORY}
    types = set(cfg.get("types", DEFAULT_TYPES)) | {UNKNOWN_TYPE}
    milestones = set(cfg.get("milestones", {}))
    stale_days = cfg.get("stale_after_days", STALE_AFTER_DAYS)

    tasks: dict[str, tuple[Path, dict]] = {}
    archive_layout: dict[str, set[str]] = {}
    for path in sorted(p for sub in ("open", "closed", "archive") for p in (root / sub).rglob("*.json")):
        r = rel(path)
        try:
            task, writable = read_task(path)
        except ValueError as e:
            out.append((r, "error", "J001", f"unreadable: {e}"))
            continue
        if not writable:
            out.append(
                (
                    r,
                    "warning",
                    "J002",
                    f"written by tadu format {task['tadu']}; this tool knows {CURRENT} and will not rewrite it",
                )
            )
            continue
        for n, kind in secret_findings(path.read_text(encoding="utf-8")):
            out.append((r, "warning", "J017", f"line {n} looks like {kind}; do not commit secrets (value not shown)"))
        errors = sorted(task_schema.iter_errors(task), key=lambda e: list(e.path))
        for e in errors:
            where = "/".join(map(str, e.path)) or "(task)"
            out.append((r, "error", "J003", f"{where}: {e.message}"))
        if errors:
            continue
        if path.read_text(encoding="utf-8") != canonical(task):
            out.append((r, "warning", "J004", "not in canonical form; `tadu fmt` rewrites it"))
        if path.stem != task["id"]:
            out.append((r, "error", "J005", f"file name does not match id {task['id']}"))
        parts = path.relative_to(root).parts
        sub = parts[0]
        if task["state"] in OPEN_STATES and sub != "open":
            out.append((r, "error", "J006", f"{task['state']} task outside open/"))
        if task["state"] not in OPEN_STATES:
            if sub == "open":
                out.append((r, "error", "J006", f"{task['state']} task still in open/"))
            if sub == "archive":
                y, m = task["closed"][:4], task["closed"][5:7]
                if parts[1:-1] not in ((y,), (y, m)):
                    out.append(
                        (r, "error", "J006", f"archived under {'/'.join(parts[1:-1])} but closed {task['closed']}")
                    )
                else:
                    archive_layout.setdefault(y, set()).add("month" if len(parts) == 4 else "year")
        if task["id"] in tasks:
            out.append((r, "error", "J007", f"id also used by {rel(tasks[task['id']][0])}"))
        tasks[task["id"]] = (path, task)
        if task["category"] not in categories:
            out.append((r, "warning", "J008", f"category {task['category']!r} is not in tadu.json"))
        if task["type"] not in types:
            out.append((r, "warning", "J009", f"type {task['type']!r} is not in tadu.json types"))
        if task.get("milestone") and task["milestone"] not in milestones:
            out.append((r, "warning", "J019", f"milestone {task['milestone']!r} is not in tadu.json milestones"))
        if task["state"] in OPEN_STATES:
            gaps = [
                f"{k} {task[k]}"
                for k, unknown in (("priority", "untriaged"), ("category", UNKNOWN_CATEGORY), ("type", UNKNOWN_TYPE))
                if task[k] == unknown
            ]
            if gaps:
                out.append((r, "warning", "J010", f"needs triage: {', '.join(gaps)}"))
        if task["state"] == "in_progress" and task.get("started"):
            days = (date.fromisoformat(today) - date.fromisoformat(task["started"])).days
            if days > stale_days:
                out.append(
                    (
                        r,
                        "warning",
                        "J018",
                        f"in progress for {days} days (started {task['started']}): finish, hand over or block it",
                    )
                )
        unknown = [k for k in task if k not in ORDER and not k.startswith("x-")]
        if unknown:
            out.append((r, "warning", "J011", f"unknown field(s) {', '.join(unknown)}; kept, but check for a typo"))
    for y, kinds in archive_layout.items():
        if len(kinds) > 1:
            out.append(
                (
                    f"todo/archive/{y}",
                    "error",
                    "J006",
                    "year mixes YYYY/ and YYYY/MM/ folders; run tadu archive --write",
                )
            )
    if (root / "archive").is_dir() and any((root / "archive").rglob("*.json")) and "archive" not in cfg:
        out.append(("todo/archive", "warning", "C003", "archive/ has tasks but tadu.json has no archive policy"))

    # relations
    for path, task in tasks.values():
        r = rel(path)
        for field, ref in references(task):
            if ref == task["id"]:
                out.append((r, "error", "J020", f"{field} points to the task itself"))
            elif ref not in tasks:
                out.append((r, "error", "J012", f"{field} {ref} is not a task of this backlog"))
        dup = task.get("duplicate_of")
        if dup in tasks and tasks[dup][1].get("duplicate_of"):
            out.append(
                (
                    r,
                    "warning",
                    "J021",
                    f"duplicate_of {dup}, which is itself a duplicate of {tasks[dup][1]['duplicate_of']}: point to the task that was kept",
                )
            )
        for b in task.get("blocked_by", []):
            if b in tasks and task["state"] in OPEN_STATES and tasks[b][1]["state"] == "cancelled":
                rep = tasks[b][1].get("superseded_by") or tasks[b][1].get("duplicate_of")
                hint = (
                    f"; it was replaced by {rep}, so block on that instead"
                    if rep
                    else "; decide whether this task still applies"
                )
                out.append((r, "warning", "J016", f"blocked_by {b} was cancelled{hint}"))
        if task["state"] in OPEN_STATES and task.get("blocked_by"):
            waiting = waiting_on(tasks, task)
            if task["state"] == "blocked" and not waiting and not task.get("blocker"):
                out.append(
                    (r, "warning", "J014", "every blocked_by task is closed: decide whether it moves to pending")
                )
            if task["state"] != "blocked" and waiting:
                out.append(
                    (r, "warning", "J015", f"{task['state']} but waits on open {', '.join(waiting)}; mark it blocked")
                )
    # cycles in blocked_by
    color: dict[str, int] = {}

    def visit(iid: str, stack: list[str]) -> None:
        color[iid] = 1
        for b in tasks[iid][1].get("blocked_by", []):
            if b not in tasks or b == iid:
                continue
            if color.get(b) == 1:
                cyc = stack[stack.index(b) :] + [b] if b in stack else [iid, b]
                out.append((rel(tasks[iid][0]), "error", "J013", "blocked_by cycle: " + " -> ".join(cyc)))
            elif b not in color:
                visit(b, [*stack, b])
        color[iid] = 2

    for iid in tasks:
        if iid not in color:
            visit(iid, [iid])
    return out


# ------------------------------------------------------------------ reading commands


def line(tasks: dict, iid: str, t: dict) -> str:
    return f"{short(tasks, iid)} [{t['state']}] {t['priority']} {t.get('due', '-')} {t['category']} {t['title']}"


def cmd_ready(d: Path, a: argparse.Namespace) -> int:
    """Open tasks that nothing blocks and nothing defers, most important first."""
    root = todo_root(d)
    tasks = load(root)
    today = today_of(a)
    rows = []
    for iid, (_, t) in tasks.items():
        if t["state"] in ("pending", "in_progress") and not waiting_on(tasks, t) and t.get("defer_until", "") <= today:
            rows.append((PRIORITY_RANK[t["priority"]], t.get("due") or "9999", t["title"], iid, t))
    for _, _, _, iid, t in sorted(rows):
        print(line(tasks, iid, t))
    return 0


def cmd_show(d: Path, a: argparse.Namespace) -> int:
    """The task file, then every relation pointing at it, which the file itself does not store."""
    root = todo_root(d)
    tasks = load(root)
    iid = resolve(tasks, a.id)
    path, task = tasks[iid]
    print(f"# {path.relative_to(root.parent)}")
    print(canonical(task), end="")
    incoming = {
        "blocks": [],
        "related (linked from)": [],
        "duplicates": [],
        "discovered": [],
        "children": [],
        "replaces": [],
    }
    for oid, (_, o) in tasks.items():
        if iid in o.get("blocked_by", []):
            incoming["blocks"].append(oid)
        if iid in o.get("related", []):
            incoming["related (linked from)"].append(oid)
        if o.get("duplicate_of") == iid:
            incoming["duplicates"].append(oid)
        if o.get("discovered_from") == iid:
            incoming["discovered"].append(oid)
        if o.get("parent") == iid:
            incoming["children"].append(oid)
        if o.get("superseded_by") == iid:
            incoming["replaces"].append(oid)
    for name, ids in incoming.items():
        for oid in sorted(ids):
            print(f"{name}: {line(tasks, oid, tasks[oid][1])}")
    return 0


# ------------------------------------------------------------------ writing commands


def save(root: Path, old_path: Path | None, task: dict, write_it: bool, what: str) -> int:
    """Validate, then write (or only report): the one place every command writes through."""
    task = {k: v for k, v in task.items() if v not in (None, "", [], {})}  # empty = absent, as written
    errors = schema_errors(task)
    if errors:
        print(f"refused, the result would be invalid: {'; '.join(errors)}")
        return 1
    target = location(root, task)
    print(what)
    if not write_it:
        print("(dry run: add --write to apply)")
        return 0
    write(target, task)
    if old_path and old_path != target:
        old_path.unlink()
    return 0


def words(text: str) -> set[str]:
    stop = {"a", "an", "the", "to", "of", "in", "on", "for", "and", "or", "with", "from", "by", "is", "it"}
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in stop and len(w) > 1}


def cmd_add(d: Path, a: argparse.Namespace) -> int:
    """Create a task. Similar existing tasks (open and closed) are shown first; the agent decides."""
    root = todo_root(d)
    tasks = load(root)
    q = words(a.title)
    scored = []
    for oid, (_, o) in tasks.items():
        w = words(o["title"])
        if q and w:
            sim = len(q & w) / (len(q) * len(w)) ** 0.5
            if sim >= 0.5:
                scored.append((sim, oid))
    for sim, oid in sorted(scored, reverse=True)[:3]:
        print(f"similar {sim:.2f}: {line(tasks, oid, tasks[oid][1])}")
    task = {
        "tadu": 2,
        "id": "t-" + str(uuid.uuid4()),
        "title": a.title,
        "state": "pending",
        "category": a.category,
        "type": a.type,
        "priority": a.priority,
        "labels": a.label or [],
        "milestone": a.milestone,
        "created": today_of(a),
        "created_by": a.created_by or os.environ.get("TADU_ACTOR"),
        "due": a.due,
        "defer_until": a.defer_until,
        "blocked_by": [resolve(tasks, x) for x in a.blocked_by or []],
        "related": [resolve(tasks, x) for x in a.related or []],
        "discovered_from": resolve(tasks, a.discovered_from) if a.discovered_from else None,
        "notes": a.note or [],
        "done_when": a.done_when or [],
        "links": a.link or [],
    }
    if task["blocked_by"]:
        task["state"] = "blocked"
    return save(root, None, task, a.write, f"add {task['id']}: {a.title}")


def parse_assignment(expr: str) -> tuple[str, str, str]:
    m = re.match(r"^([a-z_]+)(\+=|-=|=)(.*)$", expr)
    if not m:
        raise SystemExit(f"{expr!r}: use key=value, key+=value, key-=value or key=")
    return m.group(1), m.group(2), m.group(3)


def cmd_set(d: Path, a: argparse.Namespace) -> int:
    """Change fields. Lists take comma-separated values; the result is validated before writing."""
    root = todo_root(d)
    tasks = load(root)
    iid = resolve(tasks, a.id)
    path, task = tasks[iid]
    if not read_task(path)[1]:
        raise SystemExit(f"{short(tasks, iid)} was written by a newer tadu format; this tool will not rewrite it")
    new = dict(task)
    for expr in a.changes:
        key, op, value = parse_assignment(expr)
        if key in ("tadu", "id", "closed", "started"):
            raise SystemExit(f"{key} is managed by the tool")
        if key in ID_KEYS and value:
            value = resolve(tasks, value)
        if key in LIST_KEYS:
            items = [x.strip() for x in value.split(",") if x.strip()] if key not in LINE_FIELDS else [value]
            if key in ID_LIST_KEYS:
                items = [resolve(tasks, x) for x in items]
            cur = list(new.get(key, []))
            new[key] = (
                items
                if op == "="
                else cur + [x for x in items if x not in cur]
                if op == "+="
                else [x for x in cur if x not in items]
            )
        elif op == "=":
            new[key] = int(value) if key == "estimate" and value else value
        else:
            raise SystemExit(f"{key} is not a list: use {key}=value")
    if new["state"] != task["state"] and new["state"] not in OPEN_STATES:
        raise SystemExit("use close to close a task")
    if new["state"] == "in_progress" and not new.get("started"):
        new["started"] = today_of(a)
    changed = sorted(k for k in set(new) | set(task) if new.get(k) != task.get(k))
    return save(root, path, new, a.write, f"set {short(tasks, iid)}: {', '.join(changed) or 'no change'}")


def cmd_claim(d: Path, a: argparse.Namespace) -> int:
    """Take a task: assignee, in_progress and started in one change. Refused when it is not free."""
    root = todo_root(d)
    tasks = load(root)
    iid = resolve(tasks, a.id)
    path, task = tasks[iid]
    name = short(tasks, iid)
    if task["state"] not in OPEN_STATES:
        raise SystemExit(f"{name} is {task['state']}")
    if task["state"] == "blocked" or waiting_on(tasks, task):
        raise SystemExit(f"{name} is blocked: {task.get('blocker') or ', '.join(waiting_on(tasks, task))}")
    if task.get("defer_until", "") > today_of(a):
        raise SystemExit(f"{name} is deferred until {task['defer_until']}")
    others = [p for p in task.get("assignees", []) if p != a.who]
    if task["state"] == "in_progress" and others and not a.force:
        raise SystemExit(f"{name} is already in progress by {', '.join(others)} (use --force to take it over)")
    new = {
        **task,
        "state": "in_progress",
        "assignees": [a.who] if a.force else list(dict.fromkeys([*task.get("assignees", []), a.who])),
    }
    new.setdefault("started", today_of(a))
    return save(root, path, new, a.write, f"claim {name} as {a.who}")


def cmd_close(d: Path, a: argparse.Namespace) -> int:
    """Append the closing keys and move the file to closed/. Waiting tasks are only reported: never edited."""
    root = todo_root(d)
    tasks = load(root)
    iid = resolve(tasks, a.id)
    path, task = tasks[iid]
    if not read_task(path)[1]:
        raise SystemExit(f"{short(tasks, iid)} was written by a newer tadu format; this tool will not rewrite it")
    if task["state"] not in OPEN_STATES:
        raise SystemExit(f"{short(tasks, iid)} is already {task['state']}")
    closed = dict(task)
    day = a.date or today_of(a)
    if a.duplicate_of:
        keep = resolve(tasks, a.duplicate_of)
        closed.update(
            state="cancelled", closed=day, resolution=a.resolution or f"Duplicate of {keep}.", duplicate_of=keep
        )
    elif a.resolution:
        closed.update(state="cancelled", closed=day, resolution=a.resolution)
    else:
        closed.update(state="done", closed=day, result=a.result or "Done as described.", evidence=a.evidence)
    target = location(root, closed)
    plan = [f"close {short(tasks, iid)}: {path.relative_to(root)} -> {target.relative_to(root)} ({closed['state']})"]
    tasks_after = {**tasks, iid: (target, closed)}
    for oid, (_, other) in tasks.items():
        if iid not in other.get("blocked_by", []) or other["state"] not in OPEN_STATES:
            continue
        still = waiting_on(tasks_after, other)
        name = f"{short(tasks, oid)} {other['title']!r}"
        if closed["state"] == "cancelled":
            plan.append(
                f"  {name} was waiting on this task, which is cancelled, not done: review it"
                + (f" (block on {short(tasks, closed['duplicate_of'])} instead?)" if closed.get("duplicate_of") else "")
            )
        elif still:
            plan.append(f"  {name} still waits on {', '.join(short(tasks, s) for s in still)}")
        elif other.get("blocker"):
            plan.append(f"  {name}: no task blocks it any more, but it is still blocked by: {other['blocker']}")
        elif other["state"] == "blocked":
            plan.append(f"  {name}: nothing blocks it now; decide whether it moves to pending")
        else:
            plan.append(f"  {name}: nothing blocks it any more")
    return save(root, path, closed, a.write, "\n".join(plan))


def archive_plan(root: Path, today: str) -> list[tuple[Path, Path]]:
    """Moves that bring closed/ and archive/ in line with the archive policy in tadu.json."""
    policy = config(root).get("archive")
    if not policy:
        return []
    closed = []
    for p in (root / "closed").glob("*.json"):
        t, ok = read_task(p)
        if ok:
            closed.append((t["closed"], p, t))
    closed.sort(key=lambda x: x[0])
    to_archive = set()
    if "after_days" in policy:
        cutoff = (date.fromisoformat(today) - timedelta(days=policy["after_days"])).isoformat()
        to_archive |= {p for c, p, _ in closed if c < cutoff}
    if "keep_closed" in policy and len(closed) > policy["keep_closed"]:
        to_archive |= {p for _, p, _ in closed[: len(closed) - policy["keep_closed"]]}
    final = [(p, t) for _, p, t in closed if p in to_archive]
    for p in (root / "archive").rglob("*.json"):
        t, ok = read_task(p)
        if ok:
            final.append((p, t))
    per_year: dict[str, int] = {}
    months: dict[str, set[str]] = {}
    for _, t in final:
        y = t["closed"][:4]
        per_year[y] = per_year.get(y, 0) + 1
        months.setdefault(y, set()).add(t["closed"][5:7])
    need = policy.get("month_folders_min", MONTH_FOLDERS_MIN)
    by_month = {y: per_year[y] / len(months[y]) >= need for y in per_year}  # average per month that has tasks
    moves = []
    for p, t in final:
        dest = location(root, t, archived=True, by_month=by_month[t["closed"][:4]])
        if dest != p:
            moves.append((p, dest))
    return sorted(moves)


def cmd_archive(d: Path, a: argparse.Namespace) -> int:
    root = todo_root(d)
    if not config(root).get("archive"):
        print("no archive policy in tadu.json: closed tasks stay in closed/")
        return 0
    moves = archive_plan(root, today_of(a))
    for src, dst in moves:
        print(f"{src.relative_to(root)} -> {dst.relative_to(root)}")
    print(f"{len(moves)} move(s)" + ("" if a.write else " (dry run: add --write to apply)"))
    if a.write:
        for src, dst in moves:  # moved whole: the file content never changes
            dst.parent.mkdir(parents=True, exist_ok=True)
            os.replace(src, dst)
        for folder in sorted((root / "archive").rglob("*"), reverse=True):
            if folder.is_dir() and not any(folder.iterdir()):
                folder.rmdir()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="v2.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "ready", "archive"):
        p = sub.add_parser(name)
        p.add_argument("dir")
        p.add_argument("--today")
        if name == "archive":
            p.add_argument("--write", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("dir")
    s.add_argument("id")
    ad = sub.add_parser("add")
    ad.add_argument("dir")
    ad.add_argument("--title", required=True)
    ad.add_argument("--category", default=UNKNOWN_CATEGORY)
    ad.add_argument("--type", default=UNKNOWN_TYPE)
    ad.add_argument("--priority", default="untriaged")
    ad.add_argument("--label", action="append")
    ad.add_argument("--milestone")
    ad.add_argument("--due")
    ad.add_argument("--defer-until")
    ad.add_argument("--blocked-by", action="append")
    ad.add_argument("--related", action="append")
    ad.add_argument("--discovered-from")
    ad.add_argument("--note", action="append", help='one Markdown line; repeat for more ("" is a blank line)')
    ad.add_argument("--done-when", action="append")
    ad.add_argument("--link", action="append")
    ad.add_argument("--created-by", help="person id or agent:<name> (default: $TADU_ACTOR)")
    ad.add_argument("--today")
    ad.add_argument("--write", action="store_true")
    st = sub.add_parser("set")
    st.add_argument("dir")
    st.add_argument("id")
    st.add_argument("changes", nargs="+")
    st.add_argument("--today")
    st.add_argument("--write", action="store_true")
    cl = sub.add_parser("claim")
    cl.add_argument("dir")
    cl.add_argument("id")
    cl.add_argument("--as", dest="who", required=True, help="person id or agent:<name>")
    cl.add_argument("--force", action="store_true", help="take over a task someone else has in progress")
    cl.add_argument("--today")
    cl.add_argument("--write", action="store_true")
    c = sub.add_parser("close")
    c.add_argument("dir")
    c.add_argument("id")
    g = c.add_mutually_exclusive_group(required=True)
    g.add_argument("--evidence", action="append", help="one line of proof; repeat for several")
    g.add_argument("--resolution")
    g.add_argument("--duplicate-of", help="close as a duplicate of this task")
    c.add_argument("--result")
    c.add_argument("--date")
    c.add_argument("--today")
    c.add_argument("--write", action="store_true")
    a = ap.parse_args()
    d = Path(a.dir)
    if a.cmd == "check":
        findings = check(d, today_of(a))
        for path, sev, code, msg in findings:
            print(f"{path}: {sev} {code} {msg}")
        return 1 if any(sev == "error" for _, sev, _, _ in findings) else 0
    return {
        "ready": cmd_ready,
        "show": cmd_show,
        "add": cmd_add,
        "set": cmd_set,
        "claim": cmd_claim,
        "close": cmd_close,
        "archive": cmd_archive,
    }[a.cmd](d, a)


if __name__ == "__main__":
    sys.exit(main())
