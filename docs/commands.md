# Command reference

Every `tadu` command, its options and its exit status. For what the files look like, see the
format specs ([format 1](../spec/todo-format-v1.md), [format 2](../spec/todo-format-v2.md)); for
the checks `doctor` runs, see [doctor.md](doctor.md).

- [Conventions](#conventions)
- Set up: [`init`](#init) · [`sync`](#sync) · [`migrate`](#migrate)
- Read: [`list`](#list) · [`show`](#show) · [`changes`](#changes) · [`next`, `inbox`, `urgent`](#next-inbox-urgent) · [`ready`](#ready) · [`similar`](#similar) · [`feed`](#feed)
- Write: [`add`](#add) · [`mark`](#mark) · [`close`](#close) · [`set`](#set) · [`claim`](#claim)
- Maintain: [`doctor`](#doctor) · [`archive`](#archive) · [`fmt`](#fmt)
- Integrate: [`board`](#board) · [`mcp`](#mcp) · [`hook claude`](#hook-claude)

## Conventions

**One format's options.** `add`, `mark` and `close` refuse, with exit `2`, an option only the
other backlog format takes, such as `--kind` on a task backlog or `--type` on `TODO.md`; the help
marks them `format 1:` or `format 2:`.

**Dry run first.** Every command that writes (`init`, `sync`, `add`, `mark`, `close`, `set`,
`claim`, `archive`, `fmt`, `migrate`) prints what it would change and changes nothing until
`--write`. It validates before writing, so none can produce a file `doctor` would reject.

**Exit status.** `0` on success. `1` when `doctor` found an error (format 1 `add`, `mark`,
`claim` and `close` run it after writing and exit with its status), or `show` found no item or could not read
its history. `2` when the command refuses: invalid input, a target it will not
touch, or a change that would break the format; nothing is written then.

**Which repositories.** Every command but `board`, `mcp` and `hook` takes repository roots as
paths (default `.`; `set` and `claim` take them as `--root`), or `--workspace DIR` for every
repository of a [workspace](workspace-and-board.md); giving both exits `2`. A repository is
named by its directory, unless another path given has a directory of the same name: then both
are named by their full path, so `~/acme/api` and `~/globex/api` never look alike. A directory
given twice is read once. A repository that cannot be read is reported on standard error and does
not change the exit status.

**One repository.** `--repository KEY` names one of them: its workspace key, the name its items
carry, or its full path. A reading command then reads only it. A writing command changes exactly
one repository: the only one given, or the one `--repository` names; with several and none named
it exits `2` and lists them. Through a workspace, a change also needs the repository's
[`access`](workspace-and-board.md#who-may-change-what) to allow it.

**Same everywhere.** Every command here is also an [MCP tool](agents.md#mcp-server) and a call of
the [board](workspace-and-board.md#changing-items-on-the-board), with the same arguments under the
same names (`--due-before` is `due_before`), checked the same way, since both run the command
itself.

**Closed items.** Reading commands include the done and cancelled items of the last
`--done-days` days (default 14): entries of `TODO_LOG.md` and of the log's archived years
(`docs/todo-log/YYYY.md`) dated on or after that day and not before the log's `tadu:log` marker,
or tasks of `todo/closed/` and `todo/archive/`. Cancelled items are hidden unless asked for.

**Output.** Lines for people, `--json` for one JSON object per item (the keys are in the
[format 1 spec](../spec/todo-format-v1.md#tadu-list---json)). A task of a task backlog prints by
its shortest unique id prefix (`t-8c41d2e7`), and any command takes such a prefix of at least 10
characters; an ambiguous prefix is refused with the candidates listed.

**Environment.**

| Variable | Effect |
| -------- | ------ |
| `TADU_ACTOR` | who `add` records as `created_by` when `--created-by` is not given |
| `TADU_CACHE_DIR` | where the item cache lives (default `$XDG_CACHE_HOME/tadu`, else `~/.cache/tadu`) |
| `TADU_NO_CACHE` | set to turn the item cache off |

The item cache keeps what was parsed from each task file, outside the repository. Every run still
checks each file's size, inode and timestamps and rebuilds only what changed, so an edit, a
`git checkout` or a pull is always seen; files changed in the last two seconds are re-read until
they are older. It holds plain JSON, never code; delete it at any time.

---

## init

Start a backlog in a repository that has none.

```bash
tadu init                 # print the plan
tadu init --write         # format 1: TODO.md, TODO_LOG.md and the rule block
tadu init --format 2 --write   # a task backlog: todo/tadu.json and the rule block
```

| Option | Meaning |
| ------ | ------- |
| `--format {1,2}` | `1`: `TODO.md` and `TODO_LOG.md` (default); `2`: a task backlog, one JSON file per task |
| `--file FILE` | instruction file for the rule block (default `AGENTS.md`, else `CLAUDE.md`) |
| `--write` | apply instead of printing the diff |

`init` adds the rule block (as [`sync`](#sync) does), then creates `TODO.md` with the state legend
and `TODO_LOG.md` with a log marker dated today. An existing `TODO.md` or `TODO_LOG.md` is left
untouched, so it also completes a half-adopted repository; an existing rule block is updated as
`sync` would. A directory or a dangling symlink in place of either file is refused before
anything is written, with exit status `2`.

`init` writes no history index and claims no history coverage. To recover the open work buried in
past agent conversations instead, use the `tadu-create` [skill](agents.md#skills).

## sync

Write the maintenance rule into the repository's agent instruction file. See
[agents.md](agents.md#the-rule-block) for the block itself.

```bash
tadu sync .           # print the diff
tadu sync . --write   # apply it
```

| Option | Meaning |
| ------ | ------- |
| `--file FILE` | instruction file, relative to the repository root (default `AGENTS.md`, else `CLAUDE.md`) |
| `--adopt-legacy` | replace an older, unmarked section headed "Continuous TODO" |
| `--write` | apply instead of printing the diff |

- The block sits between `<!-- tadu:rule v5 -->` and `<!-- /tadu:rule -->` marker lines; only the
  text between them changes. Markers count only as a whole line outside a fenced code block, so
  quoting them in prose or in an example is safe.
- With neither `AGENTS.md` nor `CLAUDE.md` present, `sync` (and `init`) creates `AGENTS.md`. When
  both exist it uses the one that already holds the block, else `AGENTS.md`, so an `AGENTS.md`
  that a tool creates later does not move the block. Claude Code reads `AGENTS.md` only when its
  AGENTS.md support is enabled: in a repository worked with Claude Code, add a `CLAUDE.md`
  containing the line `@AGENTS.md`.
- The write goes to a temporary file in the same directory that then replaces the target, and
  only when the file still holds what `sync` read: an edit made meanwhile is kept and `sync` exits
  `2`. Line endings (LF or CRLF) and file mode are kept.
- A block that differs from the current one only in blank lines or soft line wrapping, as a
  Markdown formatter such as Prettier with `proseWrap` leaves it, counts as up to date.
- It exits `2` for a root that is not a directory, a file that resolves outside the root,
  unbalanced markers and a file that is not valid UTF-8.
- `--adopt-legacy` ends the legacy section at the next Markdown heading of any level, the next
  line starting with `<!--`, or the end of the file. Use it only when that section holds nothing
  but the standard rule; otherwise run plain `sync --write` and keep the repository's own lines
  by hand under a "TODO conventions specific to this repository" heading after the block.

## migrate

Convert a format 1 backlog into a task backlog (format 2).

```bash
tadu migrate            # print the plan
tadu migrate --write    # write todo/, then remove the converted files (git keeps them)
```

- Converts `TODO.md`, `TODO_LOG.md` and the log's archived years (`docs/todo-log/YYYY.md`), in
  that order. Archived entries become closed tasks in `todo/closed/`; `tadu archive` moves them
  once `tadu.json` has an archive policy.
- An item keeps its `ID:` as the task id; an item without one gets an id derived from its file,
  position and title, so converting twice gives the same ids. An id used twice keeps its first
  task.
- Legacy items convert to valid tasks: a title over 200 characters, or written as a bold lead
  sentence, keeps its first sentence and moves the rest into the notes; a done or cancelled item
  with no day, result, evidence or resolution gets the migration day and a "legacy item migrated
  without a recorded ..." line; a dated open item keeps its day as `created`.
- The plan lists any task that still fails the checks, so nothing is lost silently.
- The files are written into a staging folder and renamed to `todo/` at once, so an interrupted
  run leaves no half-written `todo/`. It refuses a repository that already has `todo/` or has no
  `TODO.md`, with exit status `2`.

Run `tadu sync . --write` afterwards to update the agent rules.

---

## list

Print backlog items as lines or JSON, filtered.

```bash
tadu list shop
```

```text
shop:TODO.md:10 [backlog] high **Checkout:** Reject duplicate webhook deliveries.
shop:TODO.md:14 [in_progress] - **Checkout:** Add the gift note field.
shop:TODO.md:16 [backlog/decision] high **Checkout:** Decide whether guest checkout keeps the phone field mandatory.
shop:TODO.md:26 [blocked] high **Shipping:** Switch to live carrier rates.
shop:TODO.md:38 [backlog/waiting] - **Shipping:** Carrier sends the production API key.
```

Each line is `repository:path:line [column] priority title`: `-` for no priority,
`due YYYY-MM-DD` after the priority when the item has a due date, and the item's kind in the
brackets when it has one (`[backlog/decision]`). A task of a task backlog prints as
`repository:t-8c41d2e7 [column] priority title`. The title is the item's first paragraph, so a
hard-wrapped item shows whole; a title over 160 characters is cut to 157 plus `...` here (`--json` and `show` stay full).

**Filters** (all combine):

| Option | Keeps |
| ------ | ----- |
| `--project`, `--org`, `--role` | items of a workspace project, organization, or organization role |
| `--assignee ID` | items assigned to that person |
| `--column` | `backlog`, `ready`, `in_progress`, `blocked`, `done` or `cancelled` |
| `--priority`, `--min-priority` | that priority, or that priority and above |
| `--kind` | `task`, `decision`, `waiting`, `later`, or `unclassified` (no `Kind:`) |
| `--label` | items with that label |
| `--category`, `--type` | any of the given, comma-separated |
| `--milestone` | items of that milestone (format 2) |
| `--text REGEX` | case-insensitive match over title and text |
| `--due-before DAY`, `--due-within N`, `--overdue` | due before a day, within N days (overdue included), or before today |
| `--check-before DAY` | items to look at again before that day |
| `--include-cancelled` | keep cancelled items |
| `--open` | open items only; closed ones are not even read, so it is the fastest query for pending work |
| `--history` | closed items of all time instead of `--done-days` |
| `--view NAME` | a saved view of the workspace; filters given beside it win (needs `--workspace`) |

**Order and paging.** `--sort file|priority|due|closed` orders the items. At most `--limit` print
(default 100, `0` for all), from `--offset`; when more match, a note on standard error says how
many and how to get them, so a long answer is never cut short silently. A pipe such as
`tadu list | grep` sees only that page: add `--limit 0`.

## show

Print one item by its key: its full text, then the relations that point at it (what it blocks,
its duplicates, what was discovered from it).

```bash
tadu show t-8c41d2e7
tadu show k-ea8beda0ec594e11 --json
tadu show t-8c41d2e7 --history
```

| Option | Meaning |
| ------ | ------- |
| `--json` | the same object as `list --json` |
| `--history` | also each change git recorded to the item (below) |
| `--field NAME` | only the history's changes of this field; repeat or comma-separate |
| `--since DAY`, `--until DAY` | only the history's commits from, or up to, this day (`YYYY-MM-DD`) |
| `--author TEXT` | only the history's commits whose author name contains it |
| `--done-days N` | how far back closed items are found (ignored with `--history`, which finds any) |

A task id may be a unique prefix of at least 10 characters. An item without an `ID:` field has a
derived `k-` key, which `list --json` shows; it changes when the item's title or file does. Exit
status `1` when no item has the key, or a prefix matches several tasks.

### History

`--history` prints each change git recorded to the item, newest first, uncommitted changes on
top:

```text
2026-11-18 05:21  35857cd4fc  Ana  Close the webhook fix
  file: TODO.md → TODO_LOG.md
  state: in_progress → done
  day: none → 2026-11-18
  + - Result: A replayed delivery returns 200 without a second row
  + - Evidence: pytest tests/test_webhooks.py passes

2026-11-18 05:21  dc0244ad55  Ana  Start the webhook fix
  state: pending → in_progress
```

Each change is the commit's date, short id, author and subject, then the fields that changed
(`field: before → after`) and the other lines added (`+`) or removed (`-`).

- **Markdown items** are followed by their text through `TODO.md`, `TODO_LOG.md` and the log's
  archived years, so closing, archiving, a title edit or an `ID:` added later does not lose them.
  An item without an `ID:` is matched to its earlier version by its title or by the lines it
  kept; a rewrite that changes both in one commit starts its history there. Each change costs
  one `git log -S` search in the file the item is in: well under a second for a log of a few
  hundred kilobytes, seconds for one of megabytes with thousands of commits.
- **Task files** are followed through `open/`, `closed/` and the archive's year and month
  folders, so closing and archiving show as changes of their `file`. Keys are compared one by
  one; `notes`, `done_when` and `evidence` show as lines. A task that `tadu migrate` made goes on
  with the history of the Markdown item it came from (`format: 1 → 2`). One `git log` over the
  file's few possible paths finds every change.
- **Merges** appear when they left the item unlike every parent (a conflict resolved by hand, or
  two branches' edits combined), compared with their first parent; otherwise the branches' own
  commits show the changes.
- **JSON**: with `--json` the object gains `shallow` (whether the clone is shallow) and a
  `history` list. Each entry has `commit`, `short`,
  `parents`, `date`, `author`, `subject` (`null` for uncommitted changes), `merge`, `created`,
  `path`, `changes` (`field`, `before`, `after`), `lines` (`op`, `field`, `text`), `before_text`
  and `after_text`.
- It exits `1` when the checkout is not a git repository or git is not installed. A shallow
  clone's history stops at its oldest commit, which is noted on standard error.

### Filtering the history

```bash
tadu show t-8c41d2e7 --field state --field assignee     # who took it, and when it moved
tadu show t-8c41d2e7 --since 2026-11-01 --until 2026-11-30
tadu show t-8c41d2e7 --author ana --json
```

Each filter implies `--history`, and they combine:

- `--field NAME` keeps the commits that changed one of the fields named, showing only those
  changes. Names are those the history prints: `state`, `assignees`, `priority`, `due`, `title`,
  `labels`, `file` (where the item is), and any other field or task key; `assignee` and `label`
  name the list fields. A Markdown item's other lines are the field `text`; a task's `notes`,
  `done_when` and `evidence` lines are fields of those names. `--field` repeats, or takes a
  comma-separated list.
- `--since` and `--until` keep the commits from and up to those days, both included, by the
  commit's own day (its author date where it was made). Uncommitted changes count as today.
- `--author TEXT` keeps the commits whose author name contains the text, in any case;
  uncommitted changes have no author and are left out.

With `--json` the `history` list holds the entries kept, with only the changes and lines of the
fields asked for. The MCP `show` tool and the board's History section filter by the same rules.

## changes

What changed across the backlog in a range of days, for a retro or a status report: what was
closed and by whom, what was reopened, started, blocked, created or edited.

```bash
tadu changes                                   # the last 14 days
tadu changes --since 2026-11-01 --until 2026-11-30
tadu changes --event closed,reopened --author ana
tadu changes --workspace ~/work --json
```

```text
tadu changes: 2026-11-01 to 2026-11-30 · 10 changes

Closed (1) · Ana 1
  2026-11-05  Ana  shop:t-3f2a1b4c  Ship the export.

Cancelled (1) · Ana 1
  2026-11-07  Ana  shop:t-3f2a1b4c  Ship the export.

Reopened (1) · Bob 1
  2026-11-06  Bob  shop:t-3f2a1b4c  Ship the export.  (state: done → pending)

Started (1) · Ana 1
  2026-11-03  Ana  shop:t-3f2a1b4c  Ship the export.

Blocked (1) · Bob 1
  2026-11-04  Bob  shop:t-3f2a1b4c  Ship the export.

Created (2) · Ana 2
  2026-11-01  Ana  shop:t-3f2a1b4c  Ship the export.
  2026-11-01  Ana  shop:t-55161023  Write the docs.

Changed (2) · Bob 2
  2026-11-02  Bob  shop:t-3f2a1b4c  Ship the export.  (priority: none → high)
  2026-11-02  Bob  shop:t-55161023  Write the docs.  (notes: 2 added, 1 removed)

Removed (1) · Bob 1
  2026-11-08  Bob  shop:t-55161023  Write the docs.
```

| Option | Meaning |
| ------ | ------- |
| `--since DAY`, `--until DAY` | the first and last day, both included (`YYYY-MM-DD`); by default today and the 14 days before the last day |
| `--event KIND` | only these kinds of change (below); repeat or comma-separate |
| `--author TEXT` | only commits whose author name contains it, in any case |
| `--field NAME` | only changes of these fields, as [`show --history`](#filtering-the-history) filters them |
| `--json` | one JSON object per change, newest first |

Each change is one item in one commit, grouped by kind, with how many and who made them:

| Kind | The commit |
| ---- | ---------- |
| `closed`, `cancelled` | moved the item to done, or to cancelled |
| `reopened` | moved it from done or cancelled back to an open state |
| `started`, `blocked` | moved it to in progress, or to blocked |
| `created`, `migrated` | added it; `migrated` when `tadu migrate` made it a task file |
| `changed` | changed anything else: a field, its text, its file, or its state back to pending |
| `removed` | deleted it from the backlog |

- A reopened item shows how its state went; a changed one, the fields that changed (all but
  its file) and, per field, how many lines it added and removed (`notes`, `done_when` and
  `evidence` of a task, `text` of a Markdown item).
- Days are the commits' own days (their author date where they were made), as for
  `show --history`. Only commits are read, not uncommitted changes.
- Both formats are read, and a range across `tadu migrate` too: the migration's tasks show as
  `migrated`, not as new tasks beside removed items. A Markdown item is followed into the log
  and the archived years like its history is; a task file through every folder.
- A merge shows only the changes it made itself; the branches' commits show theirs.
- One `git log` per repository walks back to the first day, and only the files each commit
  changed are read, so the cost follows the commits in the range, not the size of the backlog:
  a two-week range reads in well under a second on backlogs of thousands of items.
- With `--json` each object is a [history entry](#history) plus `repository`, `project`, `key`
  (the task id or `ID:`, `null` for an item without one), `title` and `event`.
- A repository git cannot read is reported on standard error and the others are still read.
  A first day after the last, or a bad workspace, exits `2`.

## next, inbox, urgent

Three commands answer what people ask of an agent. Each reads open items only, most pressing
first (priority, then the earliest date, then started before ready before backlog), takes
repository paths or `--workspace` and `--json`, and prints items as `list` does. On standard
error each says what else is open and which command lists it, so an agent that runs one finds the
others.

| Request | Command | Lists |
| ------- | ------- | ----- |
| "Work alone, I'll be away" | `tadu next` | tasks and unclassified items that are not blocked, not before their `Not before:` day and not assigned only to someone else |
| "What's waiting for me?", "I'm here" | `tadu inbox` | decisions, `waiting` and `later` items whose `Check on:` day or `Due:` deadline has come, any other item whose `Check on:` day has come, and the person's blocked tasks |
| "What's urgent?" | `tadu urgent` | items of urgent or high priority, and items whose `Due:` or `Check on:` is tomorrow or earlier (`--days N` widens the window) |

```bash
tadu inbox shop --person ana
```

```text
Decide: choices a person must make
shop:TODO.md:16 [backlog/decision] high **Checkout:** Decide whether guest checkout keeps the phone field mandatory.

Chase: waiting on others, follow-up due
shop:TODO.md:38 [backlog/waiting] - **Shipping:** Carrier sends the production API key.

Blocked: tasks that cannot go on
shop:TODO.md:26 [blocked] high **Shipping:** Switch to live carrier rates.
```

- `inbox` and `urgent` group items under headings that say who acts: Do, Decide, Chase, Check and
  Blocked. With `--json` each object adds a `section` key (`do`, `decide`, `chase`, `check` or
  `blocked`) to the `list` keys.
- `next` and `inbox` act for `--person ID`, else the workspace's `me`: an item assigned only to
  others is left out, and an unassigned one is anyone's. Without a person every item counts, and
  the inbox has no blocked tasks, since nobody is named on them.
- What waits on others is `tadu list --kind waiting`; what to check is the inbox's Check section,
  or `tadu list --check-before DAY`.

## ready

Print the open items nothing holds back, most urgent first: pending and in-progress items with no
open `blocked_by` task and no future `defer_until` (format 2). Takes repository paths or
`--workspace`, `--json`, `--limit` and `--offset`.

## similar

```bash
tadu similar "reject repeated webhook calls"
```

Print the open and closed items of all time most like the text, best first, each with the share
of words they have in common (0 to 1). Run it before adding an item: deciding whether one of them
is the same work is the agent's call. `--limit` (default 5) and `--open` narrow it; `--json`
prints one JSON object per item, the `list` keys and its `overlap`.

## feed

The recently-done feed: done and cancelled items of the last `--done-days` days (default 14),
newest first by their closing date, one JSON object per line with the same keys as `list --json`.
Items closed on the same day keep their repository and log order.

---

## add

Add one open item: on a task backlog a task file, otherwise an item in `TODO.md`. Like every
writing command it prints the change and writes only with `--write`, then runs `doctor`.

```bash
tadu add --title "Raise the acquirer limit or split large charges." --category Checkout \
  --kind decision --priority urgent \
  --note "Raising the limit needs a contract change; splitting ships today." --write
```

```text
- [ ] **Checkout:** Raise the acquirer limit or split large charges.

  ID: t-636b2853-f622-4fd9-accd-34ce0ce32741

  Kind: decision

  Priority: urgent

  Raising the limit needs a contract change; splitting ships today.
```

**In `TODO.md` (format 1)** the item goes last in its `## --category` section (created at the end
of the file when missing, and the title gets the `**Category:**` prefix), else at the end. It gets
a new `ID:` unless `--no-id`, then the fields given, then one paragraph per `--note`. Without
`--kind` the item is left unclassified.

| Option | Field |
| ------ | ----- |
| `--kind` | `Kind:` — `task`, `decision`, `waiting` or `later` |
| `--priority` | `Priority:` — `urgent`, `high`, `normal` or `low` |
| `--assignee` | `Assignees:` — person ids; repeat or comma-separate (also spelled `--assignees`) |
| `--due`, `--check-on`, `--not-before` | `Due:`, `Check on:`, `Not before:` — `YYYY-MM-DD` |
| `--label` | `Labels:` — slugs; repeat or comma-separate (also spelled `--labels`) |
| `--queue` | `Queue:` — `backlog` or `ready` |
| `--estimate` | `Estimate:` — minutes |

A value the fields table does not allow, a blank or multi-line argument, a category containing
`*` and a note that would read as a field, a list item or a fence exit `2` before anything is
written. A `TODO.md` with irregular line endings or an unclosed fence is refused, and so is a
change that would give `doctor` an error. The write is atomic, under an exclusive lock on the
repository, and only when the file did not change since it was read.

**On a task backlog (format 2)** `add` first shows similar open and closed tasks, then writes
`todo/open/<id>.json` with `created` and `created_by` (`--created-by`, or `$TADU_ACTOR`).

```bash
tadu add --title "Reject duplicate webhook deliveries" --category billing --type bug --priority high --write
```

`--category` and `--type` take slugs declared in `tadu.json` (`general` and `untriaged` are
always allowed), `--priority` also takes `untriaged`, and `--milestone`, `--due`, `--defer-until`,
`--queue`, `--estimate`, `--parent` and `--discovered-from` set the keys of those names. These
options take one value each time and repeat for more: `--label` and `--assignee` (a person id or
`agent:<name>`; both also comma-separate), `--blocked-by`, `--related`, `--note` (one Markdown
line; `""` is a blank line), `--done-when` and `--link`. Task ids may be unique prefixes.

## mark

Set one open item's state or fields, in either format.

```bash
tadu mark --match "over 10,000 EUR" --state blocked \
  --note 'Blocked on the decision "Raise the acquirer limit or split large charges".' --write
tadu mark --match "over 10,000 EUR" --state open --note "Decided: split charges above 10,000 EUR." --write
tadu mark --id t-8c41d2e7 --kind decision --priority high --write
```

- `--id KEY` picks the item by its key: its `ID:` or task id (a unique prefix of 10 characters or
  more will do), or the `k-` key `list --json` gives over the same repositories. `--match TEXT`
  picks the one open item whose first line (a task's title) contains it instead. No match or
  more than one exits `2` and lists the candidates.
- `--state` is `blocked` (`[!]`), `open` (`[ ]`) or `in_progress` (`[~]`); it is optional when a
  field is given. `--note` adds a paragraph at the end of the item, and blocking needs one, since
  a blocked item names its blocker.
- `--kind`, `--priority`, `--assignees`, `--due`, `--check-on`, `--not-before`, `--labels`,
  `--queue` and `--estimate` set fields, checked as `add` checks them. An existing field line is
  replaced in place; a missing one is added as the item's last paragraph. A field cannot be
  cleared this way.
- It prints the diff, writes only with `--write`, and has the same checks, lock and refusals as
  `add`.
- On a task backlog the mark becomes [`set`](#set) changes of the open task: `open` is
  `pending`, `blocked` takes the note as its `blocker` and leaving blocked drops it, another note
  is added to the notes, and `--not-before` sets `defer_until`. `--kind` and `--check-on` have no
  task key and exit `2`; use `set` for the task's own keys, such as its type.

## close

Close one open item with its proof: into `TODO_LOG.md` (format 1), or into `todo/closed/`
(format 2).

```bash
tadu close --match "Fix the header" --evidence "tests/test_header.py passes" --result "The logo shows again" --write
```

```text
- [x] 2026-10-19 — **Frontend:** Fix the header
  - Result: The logo shows again
  - Evidence: tests/test_header.py passes
```

| Option | Meaning |
| ------ | ------- |
| `--id KEY` | the item's key, as [`mark`](#mark) takes it |
| `--match TEXT` | the one open item whose first line (format 2: title) contains it |
| `--evidence TEXT` | close as done (`[x]`) with this `Evidence:` |
| `--resolution TEXT` | close as cancelled (`[-]`) with this `Resolution:` |
| `--duplicate-of ID` | format 2: cancel as a duplicate of that task |
| `--result TEXT` | the `Result:` line (format 2 default: the title) |
| `--category`, `--title` | format 1: the entry's category and text |
| `--date DAY` | the closing day (default today) |
| `--write` | apply instead of printing the diff |

One of `--id` or `--match`, and one of `--evidence`, `--resolution` or `--duplicate-of`, is
required.

**Format 1.** The item is removed from `TODO.md` with its indented continuation lines and written
into `TODO_LOG.md` as a dated entry; `close` prints the diff of both files, and after `--write`
runs `doctor` and exits with its status.

- The category is `--category`, else a `**Category:**` prefix the item already has, else the `##`
  section the item sits in, else `General`. Continuation lines of the item are kept under the
  entry, before `Result:`.
- The entry goes under the `## YYYY` heading of its date, into the `### YYYY-MM` section, else a
  `###` section headed by that very day, else a new section; missing headings are created.
  Whether it goes at the top or the bottom of its section follows the order the log already
  keeps its dates in; with no clear order it is appended.
- No match, or more than one, exits `2` and lists the candidates with their line numbers. Blank or
  multi-line values exit `2`. Each file keeps its own line endings; a file mixing CRLF and LF, or
  holding a bare CR or a Unicode line separator, is refused, and so is an item whose indentation
  leaves a code fence open.
- A close whose result would give `doctor` an error the files did not already have is refused
  before anything is written. An item that was the last one leaves `TODO.md` with its legend.
- `TODO_LOG.md` is written first, then `TODO.md`, each atomically, under an exclusive lock on the
  repository directory (POSIX) and only when neither file changed since it was read. If the
  second write fails, the message names the line to delete by hand.

**Format 2.** `close` appends `closed`, `result` and `evidence` (or `resolution`) and moves the
file to `closed/`. Closing only adds lines, so it merges with edits made on other branches. It
reports each task that waited on the closed one and changes none of them: decide whether each
moves to pending.

## set

Change fields of a task (format 2).

```bash
tadu set t-8c41d2e7 due=2026-11-20 "labels+=webhooks" --write
```

`key=value` sets a key, `key+=v` and `key-=v` add to and remove from a list, `key=` removes the
key. Moving to `in_progress` sets `started` once. `set` never changes `tadu`, `id`, `started` or
`closed`, and does not close a task: that is `close`, so a closed task always has its proof.
`--root DIR` names the repository (default `.`), or `--workspace` and `--repository`. In
`TODO.md` use [`mark`](#mark), which sets the fields an item has.

## claim

Take an item: add the person to its assignees and start it, in either format; a task also gets
`started`.

```bash
tadu claim t-8c41d2e7 --as agent:claude --write
```

It refuses a blocked, deferred (`defer_until`, `Not before:`) or closed item, and one someone
else has in progress unless `--force`, which makes the claimer its only assignee. Two agents
claiming the same item on two branches change the same lines, so the race is a git conflict,
never a silent double claim. The key is as [`mark`](#mark) takes it; `--root DIR` names the
repository, or `--workspace` and `--repository`.

---

## doctor

Check repositories against their format; it never writes. See [doctor.md](doctor.md).

```bash
tadu doctor
tadu doctor --workspace ~/work
```

It checks the roots given (default `.`). With `--workspace` it checks the files of every
repository checked out on this machine, then the workspace's items as a whole; with
`--repository` only that repository's files. `--json` prints one JSON object per finding. Exit
status `0` when there are no errors (warnings alone still exit `0`), `1` when at least one error
is reported.

## archive

Move old closed tasks to `todo/archive/YYYY/`, or `YYYY/MM/` for a busy year, as the archive
policy in `todo/tadu.json` says (format 2). Without a policy nothing moves. Files move unchanged;
the archive year and month come from each task's `closed` day.

## fmt

Rewrite task files that are not in canonical form (format 2), as `doctor` reports with `J004`.

---

## board

Serve a kanban page for a workspace, read-only unless `--allow` says more. See
[workspace-and-board.md](workspace-and-board.md).

```bash
tadu board --workspace .
```

| Option | Meaning |
| ------ | ------- |
| `--host` | address to bind (default `127.0.0.1`) |
| `--port` | port to bind; `0` for any free port (default: one derived from the workspace path) |
| `--done-days` | closed items shown (default 14; the page can change it) |
| `--allow` | what the page may do: `read` (default), `write` (add, mark, close, set and claim items) or `admin` (also `sync`, `init`, `archive`, `fmt` and `migrate`) |

## mcp

Serve the commands as [Model Context Protocol](https://modelcontextprotocol.io) tools over
standard input and output: the reading ones by default, and the writing ones with `--allow write`
(or `admin`, as for `board`). Takes repository paths or `--workspace`. See
[agents.md](agents.md#mcp-server).

## hook claude

A Claude Code `PostToolUse` hook that runs the doctor checks after an agent changes the backlog.
See [agents.md](agents.md#claude-code-hook).
