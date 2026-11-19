# Checking a backlog: `tadu doctor`

`tadu doctor` checks one or more repositories against their format and never writes. Run it by
hand, on every commit, in CI, or after every agent edit.

- [Run it](#run-it)
- [Adopt the log check](#adopt-the-log-check)
- [Enforce it](#enforce-it)
- [Finding codes](#finding-codes)

## Run it

```bash
tadu doctor .
```

```text
TODO_LOG.md:0: warning L004 no <!-- tadu:log v1 since YYYY-MM-DD --> marker; entries are checked as warnings
TODO_LOG.md:3: warning L002 entry has no Evidence: line
AGENTS.md:0: error R003 no TODO maintenance rule
```

Each finding is one line, `path:line: severity CODE message`; line `0` means the whole file. A
clean repository prints nothing.

- Exit status `0` when there are no errors (warnings alone still exit `0`), `1` when at least one
  error is reported.
- `--json` prints one JSON object per finding.
- A file that cannot be read as UTF-8 produces an `E001` finding, and the other checks and
  repositories still run.
- Without paths it checks `.`. `--workspace DIR` checks the files of every repository of a
  [workspace](workspace-and-board.md) checked out on this machine, then the workspace's items as
  a whole (the `W` codes); `--repository KEY` only that repository's files. Giving paths and
  `--workspace` together exits `2`.
- On a task backlog (format 2) `doctor` runs the `C` and `J` checks, with the history index and
  rule block checks; the format 1 `T` and `L` checks do not apply.

## Adopt the log check

Closed entries in `TODO_LOG.md` need an `Evidence:` (for `[x]`) or `Resolution:` (for `[-]`) line
with content. Without a marker the check is only a warning, so that old history does not fail. A
repository adopting the format inserts this line once, after the log header, with the adoption
date:

```text
<!-- tadu:log v1 since 2026-10-12 -->
```

Entries dated on or after that day then need proof and a missing line is an error; older entries
are legacy and are not checked. `tadu init` writes the marker with the day it runs.

## Enforce it

**pre-commit.** Pin `rev` to a tag or commit of this repository:

```yaml
repos:
  - repo: https://github.com/syntopica/tadu
    rev: <tag or commit>
    hooks:
      - id: tadu-doctor
```

**CI**, pinned to a released version, with either runner:

```bash
uvx tadu@<version> doctor .
pipx run --spec tadu==<version> tadu doctor .
```

**After every agent edit**, in Claude Code: see the [hook](agents.md#claude-code-hook).

Each fails only on errors. Warnings, including an outdated rule block, do not block a commit.

**Merging logs.** Branches that close work in the same month both append to the same section of
`TODO_LOG.md` and conflict when merged. Resolve the conflict by keeping both entries whole, then
run `tadu doctor .`. Do not set `merge=union` for these files: it can interleave the lines of two
entries and attach one entry's `Evidence:` to the other.

## Finding codes

### `TODO.md` (T)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| T001 | error | `TODO.md` is missing |
| T002 | warning | `TODO.md` does not quote the five state markers |
| T003 | error | a closed top-level item (`[x]` or `[-]`) is still in `TODO.md` |
| T004 | error | `TODO.md` is empty |

### `TODO_LOG.md` (L)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| L001 | warning | `TODO_LOG.md` is missing |
| L002 | error (warning without the log marker) | a closed `[x]` entry has no `Evidence:` content |
| L003 | error (warning without the log marker) | an obsolete `[-]` entry has no `Resolution:` content |
| L004 | warning | the `tadu:log` marker is missing |
| L005 | error | the `tadu:log` marker date does not parse |
| L006 | warning | `TODO_LOG.md` is empty |

### History index (H)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| H001 | error | an index line is not a JSON object |
| H002 | error | an index record lacks a required key |
| H003 | error | `review_status` is not one of the known statuses |
| H004 | error | two index records share a `source` and `conversation_id` |
| H005 | warning | index records are not sorted by `source`, then `conversation_id` |
| H006 | error | an index field has the wrong type or an empty value |

### Rule block (R)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| R001 | warning | there is no `AGENTS.md` or `CLAUDE.md` |
| R002 | warning | an unmarked legacy rule section exists |
| R003 | error | the instruction file has no TODO maintenance rule |
| R004 | warning | the marked rule block is older than the current version |
| R005 | error | the rule markers are not exactly one open followed by one close |

### Item fields (F)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| F001 | warning | an item field is malformed |
| F002 | warning | an `ID:` is used by more than one open item |
| F003 | warning | a field line of an open item is not read: no blank line before it, or no value |
| F004 | warning | fields of an open item contradict each other or its state, such as `Not before:` after `Due:` |

### Workspace (W)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| W001 | warning | an open item is assigned to someone who is not a person in the workspace |
| W002 | warning | an `ID:` is used in more than one repository of the workspace |
| W003 | warning | a workspace repository could not be scanned |
| W004 | error | the workspace file or local configuration is invalid |

### Files (E)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| E001 | error | a file could not be read (not valid UTF-8, or an I/O error) |

### Task backlog configuration (C)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| C001 | error | `todo/tadu.json` is missing |
| C002 | error | `todo/tadu.json` is not valid |
| C003 | warning | `todo/archive/` holds tasks but `tadu.json` has no archive policy |
| C004 | warning | a `TODO.md` next to a task backlog is ignored |

### Task files (J)

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| J001 | error | a task file is not JSON, not an object, or has no usable `tadu` version |
| J002 | warning | a task file from a newer format version: read, never rewritten |
| J003 | error | a task is invalid (missing key, bad value, or a rule of its state) |
| J004 | warning | a task file is not in canonical form; `tadu fmt` rewrites it |
| J005 | error | a task file's name differs from its id |
| J006 | error | a task is in the wrong folder for its state, or its archive year or month is wrong |
| J007 | error | two task files have the same id |
| J008 | warning | a category is not declared in `tadu.json` |
| J009 | warning | a type is not declared in `tadu.json` |
| J010 | warning | an open task needs triage: priority `untriaged`, category `general` or type `untriaged` |
| J011 | warning | a task has an unknown key (kept; probably a typo) |
| J012 | error | a relation points to a task that does not exist |
| J013 | error | `blocked_by` relations form a cycle |
| J014 | warning | a blocked task's `blocked_by` tasks are all closed and it has no `blocker` |
| J015 | warning | a pending or in-progress task waits on an open `blocked_by` task |
| J016 | warning | a `blocked_by` task was cancelled |
| J017 | warning | a line of a task file looks like a secret; the value is never printed |
| J018 | warning | a task has been in progress longer than `stale_after_days` |
| J019 | warning | a milestone is not declared in `tadu.json` |
| J020 | error | a relation points to the task itself |
| J021 | warning | `duplicate_of` points to a task that is itself a duplicate |
