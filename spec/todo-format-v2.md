# tadu format v2: one JSON file per task

Format 2 stores each task in its own JSON file under `todo/`. It exists because a single
growing `TODO.md` makes agents read only part of the backlog, and conflicts when several agents
work on parallel branches. The measurements behind it are in
[`bench/format-study/REPORT.md`](../bench/format-study/REPORT.md).

A repository uses format 2 when it has `todo/tadu.json`; otherwise it uses format 1
([`todo-format-v1.md`](todo-format-v1.md)). Every tadu command accepts both. `tadu migrate`
converts format 1 to format 2. The machine-readable schemas are
[`task.v2.schema.json`](task.v2.schema.json) and [`config.v2.schema.json`](config.v2.schema.json).

## Layout

```
todo/
  tadu.json                    format version, categories, types, milestones, policies
  open/<id>.json               pending, in_progress and blocked tasks
  closed/<id>.json             done and cancelled tasks
  archive/YYYY/<id>.json       optional: old closed tasks, moved whole
  archive/YYYY/MM/<id>.json    ...in month folders for a busy year
```

- The file name is the task id. The folder follows the state: closing moves a task from `open/`
  to `closed/`.
- A project has only `open/` and `closed/` unless `tadu.json` sets an archive policy (below).
- Nothing is ever deleted. A closed task stays the record that the work was done, or why it
  was dropped; the duplicate check and history questions search it.

## A task file

```json
{
  "tadu": 2,
  "id": "t-8c41d2e7-0a6b-4f3c-b5d8-2e9f1a7c6b43",
  "title": "Add an MCP adapter as an optional extra",
  "state": "blocked",
  "category": "board",
  "type": "feature",
  "priority": "normal",
  "labels": [
    "mcp",
    "agents"
  ],
  "milestone": "v0-2",
  "created": "2026-11-04",
  "created_by": "ana",
  "assignees": [
    "ana"
  ],
  "estimate": 240,
  "blocked_by": [
    "t-3f2a9c1e-7b4d-4e8a-9c21-5d6e7f8a9b0c"
  ],
  "notes": [
    "Core keeps no dependencies, so the adapter ships as an extra.",
    "",
    "Smallest next step: expose list and show as read-only tools in an mcp extra."
  ],
  "done_when": [
    "`pip install tadu[mcp]` serves list and show, read-only"
  ]
}
```

## Fields

Keys appear in this order, the canonical order. A key without a value is left out, never written
as `null`, `""` or `[]`.

| key | value | required | meaning |
|---|---|---|---|
| `tadu` | `2` | yes | format version of this file |
| `id` | `t-` and a lowercase UUID4 | yes | stable identity; equals the file name |
| `title` | one line, at most 200 characters | yes | what to do |
| `state` | `pending` `in_progress` `blocked` `done` `cancelled` | yes | lifecycle; format 1's `[ ]` `[~]` `[!]` `[x]` `[-]` |
| `category` | slug declared in `tadu.json`, or `general` | yes | product area; `general` = not decided |
| `type` | slug declared in `tadu.json`, or `untriaged` | yes | kind of work (`bug`, `feature`, ...) |
| `priority` | `urgent` `high` `normal` `low` `untriaged` | yes | `untriaged` = not decided; it sorts between high and normal |
| `labels` | slugs | | topics and epics |
| `milestone` | slug declared in `tadu.json` | | release or milestone |
| `created` | date | set by `tadu add` | day recorded |
| `created_by` | person id or `agent:<name>` | set by `tadu add` | who recorded it |
| `started` | date | set by tadu | first day in progress; never moved back |
| `due` | date | | deadline |
| `defer_until` | date | | not before this day: hidden from `tadu ready` until then |
| `queue` | `backlog` `ready` | | ready = can start now (pending only) |
| `assignees` | person ids or `agent:<name>` | | who works on it |
| `estimate` | whole minutes, 1 to 999999999 | | effort |
| `parent` | task id | | epic or larger task |
| `blocked_by` | task ids | | tasks that must close first |
| `related` | task ids | | same subject, no order |
| `discovered_from` | task id | | the task whose work revealed this one |
| `blocker` | one line | blocked needs it or `blocked_by` | an outside condition (a decision, a vendor) |
| `unblock` | one line | | the smallest action that would unblock it |
| `notes` | Markdown lines | | description, context, next step |
| `done_when` | Markdown lines | | acceptance criteria, usually one per line |
| `links` | URIs | | pull requests, issues, documents |
| `closed` | date | done or cancelled | day closed |
| `result` | one line | done | what changed |
| `evidence` | Markdown lines | done | the test, command, commit or PR that proves it |
| `resolution` | one line | cancelled | why it no longer applies |
| `superseded_by` | task id | | what replaced it (cancelled) |
| `duplicate_of` | task id | cancelled only | closed as a duplicate of this task |
| `files` | paths | | files the work touched |
| `x-...` | anything | | team extensions, kept untouched |

Dates are real calendar days written `YYYY-MM-DD`; slugs are lowercase letters, digits and hyphens.
One-line values hold no line break.

**Markdown lines.** `notes`, `done_when` and `evidence` store Markdown as an array with one line
per element, `""` for a blank line, read back with `"\n".join(...)`. Any Markdown round-trips,
lists and fenced code included. Two branches that edit different lines merge, where a single
string with `\n` escapes would conflict. The writer trims blank lines at the start and the end.

**Rules tied to the state.** `done` needs `closed`, `result` and `evidence`; `cancelled` needs
`closed` and `resolution`; `blocked` needs `blocker`, `blocked_by` or both. An open task has none
of `closed`, `result`, `resolution`, `superseded_by`, `duplicate_of`.

**Form.** The same task always gives the same bytes: canonical key order, unknown keys after the
known ones, `x-` keys last, two-space indent, one array element per line, UTF-8, final newline.
There is no `updated` field: every parallel edit would conflict on it, and git already records it.

## `todo/tadu.json`

```json
{
  "tadu": 2,
  "categories": { "board": "Board", "docs": "Docs" },
  "types": ["bug", "feature", "chore", "test", "docs", "refactor", "perf", "security", "decision"],
  "milestones": { "v0-2": { "name": "0.2", "due": "2026-12-15" } },
  "stale_after_days": 14,
  "archive": { "after_days": 180, "keep_closed": 500, "month_folders_min": 10 }
}
```

- `tadu` and `categories` (slug to display name) are required. `general` is always allowed.
- `types` defaults to bug, feature, chore, test, docs, refactor, perf, security; `untriaged` is
  always allowed.
- `milestones`: slug to `{name, due}`; a task's milestone must be declared.
- `stale_after_days` (default 14): doctor warns about a task in progress for longer.
- `archive` (optional): `after_days` archives tasks closed longer ago than that, `keep_closed` keeps
  at most that many in `closed/`. Either rule, or both. `month_folders_min` (default 10): a year
  gets month folders only when its months would average at least that many tasks, counting months
  that have tasks, so a quiet year stays one folder. Archiving uses the `closed` date in the file,
  never file times.
- Any other key is an error, except `x-` keys.

## Relations

A task stores its outgoing relations; `tadu show` computes the reverse ones, so a relation lives in
one file and cannot drift out of sync.

| stored | meaning | shown on the other task |
|---|---|---|
| `blocked_by` | must close first | blocks |
| `related` | same subject | related (linked from) |
| `discovered_from` | found while doing that task | discovered |
| `parent` | part of that task | children |
| `superseded_by` | replaced by (cancelled) | replaces |
| `duplicate_of` | the same work (cancelled) | duplicates |

`tadu ready` lists open tasks that no open `blocked_by` task and no future `defer_until` holds
back. Closing a task reports each task that waited on it and changes none of them: the agent
decides whether a freed task moves to `pending`. Until it does, doctor lists it (J014).

## Ids

Files store the full id, 122 random bits, generated on any branch without coordination; short
stored ids would collide (with 8 hex digits, a 10% chance at 30,000 tasks). Commands show the
shortest unique prefix of at least 8 hex digits (`t-8c41d2e7`) and accept one. A prefix that
matches several tasks is refused with the candidates listed, never guessed. Two branches creating
the same id would create the same file: git reports the conflict and doctor reports J007.

## Commands

Every command that writes is a dry run until `--write`, and writes through the same validation,
so none can produce a file doctor would reject.

| command | what it does |
|---|---|
| `tadu init --format 2` | creates `todo/tadu.json` and the agent rule block |
| `tadu migrate` | converts `TODO.md` and `TODO_LOG.md` into task files, then removes them (git keeps their history) |
| `tadu add --title T --category C --type Y --priority P` | shows similar open and closed tasks first, then writes `open/<id>.json` with `created` and `created_by` (`--created-by` or `$TADU_ACTOR`) |
| `tadu set ID key=value ...` | changes fields; `key+=v` and `key-=v` for lists, `key=` to remove; moving to `in_progress` sets `started` once |
| `tadu claim ID --as WHO` | sets the assignee, `in_progress` and `started` at once; refused for a blocked, deferred or closed task, or one someone else has in progress (`--force` takes it over) |
| `tadu close --id ID --evidence E` | appends `closed`, `result` (default: the title) and `evidence`, moves the file to `closed/`, reports the tasks that waited on it; `--resolution R` or `--duplicate-of ID` cancel instead |
| `tadu archive` | applies the archive policy, moving files unchanged |
| `tadu fmt` | rewrites files that are not in canonical form |
| `tadu list`, `show`, `ready`, `similar`, `feed`, `board` | read both formats |

`tadu set` never changes `tadu`, `id`, `started` or `closed`, and does not close a task: that is
`tadu close`, so a closed task always has its proof. Two agents claiming the same task on two
branches change the same lines, so the claim race is a git conflict, never a silent double claim.

## Doctor

`tadu doctor` runs these checks on a repository with `todo/tadu.json`, with the history index and
rule block checks; format 1's TODO and log checks do not apply.

| code | severity | finding |
|---|---|---|
| C001 | error | `todo/tadu.json` is missing |
| C002 | error | `todo/tadu.json` is not valid |
| C003 | warning | `archive/` holds tasks but there is no archive policy |
| C004 | warning | a `TODO.md` next to a task backlog is ignored |
| J001 | error | a task file is not JSON, not an object, or has no usable `tadu` version |
| J002 | warning | a task file from a newer format version: read, never rewritten |
| J003 | error | a task is invalid (missing key, bad value, state rule) |
| J004 | warning | a task file is not in canonical form; `tadu fmt` fixes it |
| J005 | error | the file name differs from the id |
| J006 | error | a task is in the wrong folder for its state, or its archive year or month is wrong, or a year mixes both layouts |
| J007 | error | two files have the same id |
| J008 | warning | a category not declared in `tadu.json` |
| J009 | warning | a type not declared in `tadu.json` |
| J010 | warning | an open task needs triage: priority `untriaged`, category `general` or type `untriaged` |
| J011 | warning | an unknown key (kept; probably a typo) |
| J012 | error | a relation points to a task that does not exist |
| J013 | error | a `blocked_by` cycle |
| J014 | warning | blocked, but every `blocked_by` task is closed and no `blocker` is set |
| J015 | warning | pending or in progress while a `blocked_by` task is still open |
| J016 | warning | a `blocked_by` task was cancelled (block on its replacement when it has one) |
| J017 | warning | a line looks like a secret (private key, cloud or API key, token, password in a URL, credential assignment); the value is never shown |
| J018 | warning | in progress for longer than `stale_after_days` |
| J019 | warning | a milestone not declared in `tadu.json` |
| J020 | error | a relation points to the task itself |
| J021 | warning | `duplicate_of` points to a task that is itself a duplicate |

## Versions

Every file carries its version. A reader upgrades older files through small steps, so a later tool
still opens a version-2 file; format 1 is Markdown and is converted once by `tadu migrate`. A tool
never rewrites a file with a newer version than it knows: it reads the keys it understands and
reports J002, so agents on different tadu versions cannot strip each other's fields. Unknown keys
are kept on rewrite. The version only changes for a breaking change; new optional keys do not
change it.
