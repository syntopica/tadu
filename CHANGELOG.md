# Changelog

## 0.2.0

### Compatibility

Existing backlogs read as before: `list`, `show`, `feed` and `doctor` print the
same text and findings for files without the new fields, and every JSON object
keeps its keys and values, with `kind`, `check_on` and `not_before` added
(`null` when absent).

- The rule block is v4. Repositories synced with v3 get an `R004` warning until
  `tadu sync . --write` updates them.
- Repositories given as paths whose directories share a name are named by their
  full path in `list`, `next`, `inbox`, `urgent`, `show` and `feed`, and in the
  derived `k-` keys of their items, so two checkouts named `api` stay apart. A
  directory given twice is read once.

### Added

- The `Kind:` item field: `task`, `decision`, `waiting` or `later`. An item
  without it is unclassified (`kind` null); no kind is guessed from the text.
  `list --kind` (with `unclassified`), the `kind` key of `list --json` and of
  saved views, and list lines that show a kind as `[backlog/decision]`.
- The `Check on:` and `Not before:` date fields, apart from the `Due:`
  deadline: the day to look at an item again, and the day before which it
  cannot start. `list --check-before` and the `check_before` view key.
- `F004` warns about fields that contradict each other or the item's state:
  `Not before:` or `Check on:` after `Due:`, an item in progress whose
  `Not before:` is ahead or whose kind is `later`, and `Queue: ready` on a
  `waiting` or `later` item. `F001` and `F003` cover the new fields.
- `tadu next`, `tadu inbox` and `tadu urgent`: what an agent can do without a
  person, what waits on a person (decisions, checks and follow-ups whose day
  has come, blocked tasks), and what is urgent or due, grouped by who acts.
  Items whose `Not before:` is ahead are left out of all three.
- `tadu add` puts a new item into `TODO.md`, and `tadu mark` sets an open
  item's state (`blocked` with its blocker named, `open`, `in_progress`). Both
  print a diff and write only with `--write`.
- `tadu mcp`, a Model Context Protocol server on standard input and output with
  the tools `next`, `inbox`, `urgent`, `list`, `show`, `add`, `mark` and
  `close`, and instructions that tell an agent when to use them. No new
  dependencies.
- `list --open` and the `open` key of saved views leave out closed items.
- Board: a Kind filter, chip, grouping and detail field; a badge on decision,
  waiting and later items; a "Needs a person" sidebar section (Waiting on me,
  Decisions, Waiting on others, Later) with counts in the current scope.

### Changed

- Board: "Waiting on me" shows what `tadu inbox` lists for `me` (decisions,
  due follow-ups and checks, blocked tasks assigned to me) instead of only
  blocked items assigned to me.
- Board: the priority and kind badges are left out where the list already
  names them, when grouped by that attribute or filtered to one value of it.

### Fixed

- `tadu sync --write` no longer overwrites an instruction file edited after it
  was read; it exits `2` and keeps the edit. A failed write is reported instead
  of raising a traceback.
- The "changed since read" message names the files and no longer says
  "closing" for every command.
