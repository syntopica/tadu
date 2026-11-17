# tadu task format v2: one JSON file per task (draft proposal)

Status: **implemented in tadu** as format 2: see [spec/todo-format-v2.md](../../../spec/todo-format-v2.md)
and the README. This draft and its prototype (`v2.py`) are kept as the record of how the format was
designed; the spec is the reference. Nothing in this repository's own backlog was migrated.

Original status: draft for discussion. Machine-readable schemas:
[`task.v2.schema.json`](task.v2.schema.json) and [`config.v2.schema.json`](config.v2.schema.json).
Examples: [`examples/todo/`](examples/todo/). Prototype commands:
`python v2.py check|ready|show|add|set|claim|close|archive`. Converter from tadu v1 Markdown:
`python migrate_v1.py SRC OUT`. Scenario tests: `python test_v2.py` (34 pass). What other systems store:
[`field-survey.md`](field-survey.md).

Decisions taken:

- `type` is its own field.
- `priority`, `category` and `type` are required, with defaults for "not decided yet": `untriaged`,
  `general` and `untriaged`.
- The archive is optional.
- Archive folders are per year, split into months only when the months would hold at least 10 tasks
  on average.
- Ids must not collide.
- Tasks can be `blocked_by` other tasks; closing a task only *reports* the tasks it frees, and the agent decides.
- From the [field survey](field-survey.md), all nine additions are adopted:
  - `duplicate_of`, `related` and `discovered_from` relations;
  - a `started` date set by the tool;
  - `milestone`, declared in `tadu.json`;
  - `links`;
  - `defer_until`;
  - `created_by`;
  - a `claim` command.

## Layout

```
todo/
  tadu.json                         repository settings: version, categories, types, archive policy
  open/<id>.json                    pending, in_progress and blocked tasks
  closed/<id>.json                  done and cancelled tasks
  archive/YYYY/<id>.json            optional: old closed tasks, moved whole
  archive/YYYY/MM/<id>.json         ...split into months only for a year with many tasks
```

- The file name is the task id. The folder follows the state: closing moves a task from `open/` to `closed/`.
- **A normal project has only `open/` and `closed/`.** The archive exists only when `tadu.json` has an
  `archive` policy, for old or large projects:

  ```json
  "archive": { "after_days": 180, "keep_closed": 500, "month_folders_min": 10 }
  ```

  `after_days` archives tasks closed longer ago than that. `keep_closed` caps `closed/` and archives the oldest
  beyond the cap. Either rule, or both. `month_folders_min` (default 10) splits a year into month folders
  only when its months would hold at least that many tasks on average, counting months that have tasks.
  Twelve tasks in a year stay in one folder; 120 in a year, or 20 in two months, get month folders.
  `tadu archive --write` applies it: files move whole and unchanged, and a year that becomes busy enough
  is reorganised into months in the same commit. Without `--write` it only prints the moves.
- The archive is never deleted. Everyday queries can skip it; the duplicate check and history
  questions always include it.
- Ageing uses the `closed` date inside the file, never file times (a git checkout resets them).
  `tadu doctor` reports what is due and never writes.

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
  "related": [
    "t-b7e3a915-4c2d-4a8f-8e61-0f9d3c2b1a57"
  ],
  "notes": [
    "Core keeps no dependencies, so the adapter ships as an extra.",
    "",
    "Smallest next step: expose list and show as read-only tools in an mcp extra."
  ],
  "done_when": [
    "`pip install tadu[mcp]` serves list and show, read-only",
    "`uv run pytest` passes with and without the extra"
  ],
  "links": [
    "https://modelcontextprotocol.io/specification"
  ]
}
```

## Fields

Keys appear in this order (the canonical order). Keys without a value are left out, never written
as `null`, `""` or `[]`.

| key | type | required | meaning | tadu v1 equivalent |
|---|---|---|---|---|
| `tadu` | integer, `2` | yes | format version of this file | (implicit: Markdown is v1) |
| `id` | `t-` + lowercase UUID4 | yes | stable identity; equals the file name (see Ids) | `ID:` field, or a derived key |
| `title` | one line, ≤ 200 chars | yes | what to do, imperative | first line after the marker |
| `state` | `pending` `in_progress` `blocked` `done` `cancelled` | yes | lifecycle | `[ ]` `[~]` `[!]` `[x]` `[-]` |
| `category` | slug from `tadu.json`, or `general` | **yes** | product area (`ui`, `billing`); `general` = not decided | `**Category:**` prefix or `##` section (none → `general`) |
| `type` | slug from `tadu.json`, or `untriaged` | **yes** | kind of work (`bug`, `feature`…); `untriaged` = not decided | (was mixed into Labels or prose; none → `untriaged`) |
| `priority` | `urgent` `high` `normal` `low` `untriaged` | **yes** | `untriaged` = not decided yet | `Priority:` (none → `untriaged`) |
| `labels` | slugs | – | topics, epics (`dark-mode`) | `Labels:` |
| `milestone` | slug from `tadu.json` milestones | – | release or milestone it belongs to | – (new) |
| `created` | `YYYY-MM-DD` | set by `tadu add` | day recorded | – (new) |
| `created_by` | person id or `agent:<name>` | set by `tadu add` | who recorded it (`ana`, `agent:claude`) | – (new) |
| `started` | `YYYY-MM-DD` | set by the tool | day work began: the first move to `in_progress`, kept after | – (new) |
| `due` | `YYYY-MM-DD` | – | deadline | `Due:` |
| `defer_until` | `YYYY-MM-DD` | – | not before this day: hidden from `ready` until then | – (new) |
| `queue` | `backlog` `ready` | – | ready = can start now; pending only | `Queue:` |
| `assignees` | person ids or `agent:<name>` | – | who works on it; `tadu claim` sets it | `Assignees:` |
| `estimate` | minutes | – | effort | `Estimate:` |
| `parent` | task id | – | epic or parent task | – (new) |
| `blocked_by` | task ids | – | tasks that must close first (see Relations) | free-text `Depends on:` |
| `related` | task ids | – | same subject, no order between them | – (new) |
| `discovered_from` | task id | – | the task whose work revealed this one | – (new) |
| `blocker` | one line | blocked needs this or `blocked_by` | an external condition (a decision, a vendor) | prose under a `[!]` item |
| `unblock` | one line | – | smallest action that would unblock it | "Smallest unblock:" prose |
| `notes` | Markdown as an array of lines | – | description, context, next step, code, lists | continuation lines |
| `done_when` | Markdown lines | – | acceptance criteria, usually one per line | "Done when:" prose |
| `links` | URIs | – | pull requests, issues, documents, designs | links inside prose |
| `closed` | `YYYY-MM-DD` | if done or cancelled | day closed; drives archiving | date in the log entry |
| `result` | one line | if done | what changed | `- Result:` |
| `evidence` | Markdown lines | if done | test, command, commit, PR, usually one per line | `- Evidence:` |
| `resolution` | one line | if cancelled | why it no longer applies | `- Resolution:` |
| `superseded_by` | task id | – | what replaced it | prose |
| `duplicate_of` | task id | only when cancelled | closed as a duplicate of this task | prose |
| `files` | paths | – | files the work touched | `- Files:` |
| `x-…` | anything | – | team extensions (`x-jira`) | – |

Rules the schema enforces:

- `priority`, `category` and `type` are required, each with a value for "not decided yet":
  `untriaged`, `general` (already tadu's fallback category) and `untriaged`. Migration uses them for v1
  items that lack the information, and a quick capture can use them. They are always allowed, whatever
  `tadu.json` declares, and `doctor` lists every open task that still has one (J010, "needs triage").
  An untriaged priority sorts after `high` and before `normal`, so unknown work surfaces instead of sinking.
- `duplicate_of` only appears on a cancelled task. `started`, `closed`, `id` and `tadu` are managed
  by the tool; `tadu set` refuses to change them.
- `done` needs `closed`, `result` and `evidence`; `cancelled` needs `closed` and `resolution`;
  `blocked` needs `blocker`, `blocked_by`, or both. An open task carries none of the closing keys.
- `notes`, `done_when` and `evidence` are Markdown split into lines: one array element per line,
  `""` for a blank line, no line break inside an element. Readers rebuild the text with
  `"\n".join(...)`. Any Markdown, lists and fenced code included, round-trips exactly. The writer trims
  blank lines at the start and end; blank lines inside are content.
- Dates are real calendar-shaped `YYYY-MM-DD`; ids match the UUID4 pattern; slugs are lowercase
  letters, digits and hyphens; text fields are single lines.

Rules `v2.py check` (the future `tadu doctor`) adds, because they need more than one file:

| code | severity | finding |
|---|---|---|
| C001 / C002 | error | `todo/tadu.json` missing or invalid |
| J001 | error | file is not JSON or has no integer `tadu` version |
| J002 | warning | file from a newer format version: read-only for this tool |
| J003 | error | schema violation (missing evidence, bad date, two-line title…) |
| J004 | warning | not in canonical form; `tadu fmt` rewrites it |
| J005 | error | file name differs from `id` |
| J006 | error | file in the wrong folder for its state, or archived under the wrong month |
| J007 | error | the same `id` in two files |
| J008 / J009 | warning | category or type not declared in `tadu.json` |
| J010 | warning | open task that needs triage: priority `untriaged`, category `general` or type `untriaged` |
| J011 | warning | unknown key (kept; probably a typo such as `prority`) |
| J012 | error | a relation (`parent`, `blocked_by`, `related`, `discovered_from`, `superseded_by`, `duplicate_of`) points to a task that does not exist |
| J013 | error | `blocked_by` cycle (A waits on B, B waits on A) |
| J014 | warning | blocked, but every `blocked_by` task is closed and there is no `blocker`: decide whether it moves to pending |
| J015 | warning | pending or in progress while a `blocked_by` task is still open: mark it blocked |
| J016 | warning | a `blocked_by` task was cancelled: block on its replacement, or decide whether this still applies |
| J018 | warning | in progress longer than `stale_after_days` (default 14) since `started`: finish, hand over or block it |
| J019 | warning | `milestone` not declared in `tadu.json` |
| J020 | error | a relation points to the task itself |
| J021 | warning | `duplicate_of` points to a task that is itself a duplicate: point to the one that was kept |
| J017 | warning | a line looks like a secret (private key block, AWS, GitHub, Slack, OpenAI/Anthropic, Stripe or Google key, JWT, credential assignment); the finding names the line and the kind, never the value |
| C003 | warning | `archive/` holds tasks but `tadu.json` has no archive policy |

J006 also covers a year whose archive mixes `YYYY/` and `YYYY/MM/` folders.

## Why it looks like this

- **One field per line, closing keys last.** Different fields merge independently, and closing a
  task only appends keys. Measured: 150/150 clean merges on different tasks, and 50/50 when one branch
  closes a task that another branch edits (REPORT 8.1).
- **Multi-line text as an array of lines, not one string with `\n`.** This is the "array of lines,
  `join("\n")` at runtime" pattern: readable, diff-friendly, and any JSON parser reads it. Tested: two
  branches editing different parts of a task's notes merged cleanly as an array, but conflicted as one
  escaped string or as base64, where everything is one long line. Agents never write `\n` escapes; a raw
  newline in a JSON string was the one JSON slip found in REPORT 8.2. Lines, rather than paragraphs,
  keep code blocks and lists intact.
- **Never hand-roll the JSON.** Files are written by the tool through a JSON library, in canonical form.
  Agents create and change tasks with `tadu add` / `tadu set` / `tadu close`. If a file is edited by hand,
  `tadu doctor` reports the slip (every one of the slips injected in REPORT 8.2 was reported) and `tadu fmt`
  restores the canonical form.
- **No secrets in tasks.** Task files are committed and read by every agent, so `doctor` warns when a
  line looks like a key or token (J017). It never prints the value, because doctor output ends up in agent
  context and CI logs. Keys belong in environment variables or a secret manager, referenced by name.
- **Canonical form.** Fixed key order, two-space indent, one array element per line, UTF-8, final
  newline: the same task always gives the same bytes, so a diff shows only real changes.
- **No `updated` timestamp.** Every edit on every branch would change that one line, turning all
  parallel edits of a task into conflicts. Git already records when a file changed.
- **Relations are ids; reverse links are computed.** "What does X block" is derived by the tool from
  `blocked_by`. Storing both directions would need two files kept in sync.
- **`type` is separate from `labels`.** "Open bugs" becomes an exact filter, and the allowed types
  are declared once in `tadu.json`.

## Relations

A task stores its outgoing relations; the reverse directions are computed, never stored, so a
relation lives in one file and cannot drift out of sync:

| stored on the task | meaning | computed on the other task (`tadu show`) |
|---|---|---|
| `blocked_by: [ids]` | must close first | blocks |
| `related: [ids]` | same subject, no order | related (linked from) |
| `discovered_from: id` | found while doing that task | discovered |
| `parent: id` | part of an epic or larger task | children |
| `superseded_by: id` | replaced by (cancelled) | replaces |
| `duplicate_of: id` | the same work (cancelled) | duplicates |

`tadu close X --duplicate-of Y` closes X as cancelled with `duplicate_of: Y`. This is how the
duplicate check (`tadu add` shows similar tasks first) is resolved when a twin slips through anyway.

For `blocked_by`, only this direction is stored; "what does X block" is computed. The tool then does the bookkeeping an agent should not have
to remember:

- `tadu ready` lists open tasks that nothing blocks (no open `blocked_by` task), most important first.
  "What can I work on now?" becomes one command.
- `tadu close X` **reports** every task that was waiting on X and changes none of them. The agent
  decides, because it can judge what a file cannot: whether the work is really unblocked, or whether
  something else came up.

  ```
  close t-3f2a9c1e: open/t-3f2a9c1e-….json -> closed/t-3f2a9c1e-….json (done)
    t-8c41d2e7 'Add an MCP adapter as an optional extra': nothing blocks it now; decide whether it moves to pending
  ```

  The other cases are reported the same way. A task that still waits on another open task: "still waits
  on t-…". A task that also has an external `blocker`: "no task blocks it any more, but it is still
  blocked by: …". If X was *cancelled* rather than done: "cancelled, not done: review it", and J016
  suggests the replacement when X has `superseded_by`. Until the agent acts, `doctor` keeps listing
  a freed task (J014), so a decision is not lost when the session ends.
- `doctor` catches inconsistent states: cycles (J013), tasks that could be unblocked (J014), tasks that wait
  on open work but are not marked blocked (J015), and references to missing tasks (J012). Archived tasks
  still resolve as targets.

When the agent moves a freed task to `pending`, it edits only the `state` line of that task's file,
which merges with other edits to the task like any field change.

## Ids

Files store the full id, `t-` plus a UUID4: 122 random bits, generated independently on every branch
with no coordination. Storing only a short id would collide: with 8 hex digits, the chance of
a duplicate is 10% at 30,000 tasks and 69% at 100,000 (birthday bound). Even 12 digits is not
safe forever. The tool *displays* the shortest unique prefix, at least 8 hex digits (`t-8c41d2e7`), and
lengthens it when two tasks share one, as git does with commits. In the synthetic data, 8 digits were enough for
27,500 tasks. An ambiguous prefix is refused with the candidates listed, never guessed. If two branches
ever did create the same id, they would create the same file name: git reports an add/add conflict and
`doctor` reports J007, so it can never merge silently.

## Lifecycle, as the CLI would do it

| command | what changes |
|---|---|
| `tadu add` | shows similar open and closed tasks first (the agent decides); writes `open/<id>.json` with `created` and `created_by` (`--created-by`, or `$TADU_ACTOR`), validated |
| `tadu set ID key=value …` | fields in place; `key+=v` / `key-=v` for lists, `key=` to remove; validated before writing; moving to `in_progress` sets `started` once |
| `tadu claim ID --as WHO` | `state: in_progress`, the assignee and `started`, in one change. Refused when the task is blocked, deferred or in progress by someone else (`--force` takes it over). Two agents claiming on two branches make a git conflict, never a silent double claim |
| `tadu ready` | nothing changes: lists open tasks that nothing blocks and nothing defers |
| `tadu show ID` | nothing changes: the task and every relation pointing at it |
| `tadu close` | `state`, then `closed` + `result` + `evidence` (or `resolution`, or `--duplicate-of`) appended; file moves to `closed/`; waiting tasks reported, never changed |
| `tadu archive --write` | only with an archive policy: old closed tasks move whole to `archive/YYYY/` (or `YYYY/MM/`) |

Every write command is a dry run without `--write`, and every write goes through the same
validation, so no command can produce a file that `doctor` would reject.

## Versioning

- Every file carries `"tadu": N`. The repository's `tadu.json` says which version new files use.
- **Read old, write new:** readers upgrade a file through a chain of small steps (v2→v3, v3→v4…), so a
  v12 tool opens a v2 file without keeping a v2 parser. v1 is the Markdown format, converted once by
  `migrate_v1.py`.
- **Never rewrite a newer file:** a tool that knows version 4 reads a version-5 file as far as it can
  and refuses to write it, so different agents on different tadu versions cannot strip each other's fields.
- **Unknown keys are kept** on rewrite, for the same reason (and reported, in case of a typo).
- **A version bump only for breaking changes** (a renamed key, a changed meaning). New optional keys do not bump it.
- **Bulk upgrades** run as `tadu migrate`, in a commit of their own.

## Checked

- `examples/todo/` (blocked by another task with a milestone, links and a related task; an untriaged
  capture by an agent, deferred and discovered from another task, with a fenced shell snippet; an
  external blocker; in progress by a person and an agent with a start date; done; a duplicate;
  archived cancelled) validates. The only finding is the intended
  J010 for the untriaged capture.
- `test_v2.py`, 34 scenarios, all pass. The 12 added for the survey fields:
  - close as a duplicate (`show` lists the duplicates, the waiting task is pointed at the kept one);
  - duplicate rules (cancelled only, chains, self-reference);
  - `related` and `discovered_from` shown from both sides;
  - `started` set once and stale work reported;
  - milestones declared; links must be URIs; `created_by` accepts people and agents;
  - `defer_until` hides a task from `ready` and `claim`;
  - `claim` refuses blocked and taken tasks, `--force` takes over, and two agents claiming on two
    branches conflict in git;
  - `add` shows similar tasks and writes a valid file;
  - `set` validates before writing.

  The earlier 22:
  - Relations and close: close reports a freed task and leaves it for the agent, and `ready` follows;
    close only appends lines; two blockers need both closed; an external blocker keeps a task blocked;
    a cancelled blocker asks for review; cycles, missing targets, stale blocked tasks and unmarked waiting
    tasks are reported.
  - Fields: priority, category and type are required, and their "not decided" values are listed for triage.
  - Archive: no policy means no archive; archiving works by age and by count; month folders appear only
    for years averaging at least 10 tasks per month; mixed layouts are reported.
  - Ids and versions: ambiguous prefixes are refused; newer-version files are never rewritten.
  - Line fields: any Markdown round-trips; an element with a line break is rejected; blank edge lines are
    trimmed by the writer and flagged if hand-written; two branches editing different lines of the notes
    merge in git.
  - Secrets are flagged by line and kind without being shown, and ordinary text ("API keys page",
    "token refresh") is not.
  - Migration fills the defaults and keeps v1 wrapping, lists, code blocks, "Done when" and the blocker exactly.
- Earlier checks: eight deliberately broken files, each reported with the expected code.
- tadu's own `TODO.md` + `TODO_LOG.md` converted (to `/tmp`, the repository is unchanged): 7 open and 23
  closed tasks, no archive (no policy). 0 errors, no secret warnings; 7 J010 "needs triage", one per open
  task. Long v1 titles keep their first sentence, and the rest opens the notes.
- The synthetic 600-open / 6,000-closed backlog: 6,600 files, 0 errors, no secret false positives; the only
  warnings are the 213 open tasks without a priority. With `--archive-after-days 30` and `v2.py archive
  --write`, 5,656 tasks are archived and both years get month folders.

## Still open

Nothing in the format itself. The next step would be a plan for the tadu changes (format v2 support in
`list`, `show`, `board`, `doctor` and `close`; new `add`, `ready`, `archive`, `fmt`, `migrate`; rule block v4),
to agree on before any migration.
