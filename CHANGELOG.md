# Changelog

## Unreleased

### Added

- `tadu show KEY --history` prints each change git recorded to a Markdown
  backlog item, newest first, with the fields that changed and the lines added
  or removed, uncommitted changes first; `--json` adds a `history` list. Items
  are followed through `TODO.md` and `TODO_LOG.md` by their text, so closing,
  a title edit or a later `ID:` does not lose them, and merges that combined or
  resolved changes are shown. A task file's history covers `open/`, `closed/`
  and the archive's year and month folders, compares its keys one by one, and
  goes on before `tadu migrate` with the Markdown item the task came from.
- The MCP `show` tool takes `history` (boolean) to add the item's history.
- `tadu changes`: what changed across the backlog in a range of days (the last
  14 by default), for a retro: each item's change in each commit, grouped as
  closed, cancelled, reopened, started, blocked, created, migrated, changed or
  removed, with who made them; `--event`, `--author`, `--field` and `--json`.
  Both formats, and ranges across a migration. The MCP `changes` tool and the
  board's Changes view show the same.
- `show --history` filters: `--field` (such as `state` or `assignee`),
  `--since`, `--until` and `--author`, each implying `--history`; the MCP
  `show` tool takes `field`, `since`, `until` and `author`, and the board's
  History section has the same filters, applied without reading git again.
  History lines in JSON name their `field`.
- The board's item detail has a folded History section with the same entries,
  read from git only when it is opened.
- Closed entries archived under `docs/todo-log/YYYY.md` are read with the log:
  `list --history`, `show` and the other commands find them within their date
  window, under the log's `tadu:log` marker. An archived entry's history runs
  from the archiving commit back through the log.
- `tadu migrate` also converts the log's archived years into closed tasks and
  removes them with `TODO.md` and `TODO_LOG.md`.
- One declaration per command drives the command line, the MCP tools and the
  board: the same arguments under the same names, the same choices and help,
  the same checks, since MCP and the board run the command itself.
- The MCP server offers every command as a tool: `ready`, `similar`, `feed`,
  `doctor`, `set` and `claim` are new, `list` takes all its filters, `show`
  and `similar` take `json`, `add` and `close` their format 2 options. Every
  tool takes `repository`, and a change takes `preview` to see it first.
- Permissions: `tadu mcp --allow` and `tadu board --allow` take `read` (the
  default), `write` (add, mark, close, set, claim) or `admin` (also sync, init,
  archive, fmt, migrate). A workspace repository can be limited with
  `access = "read"` or `"write"`, for every change made through the workspace:
  board, MCP or command line.
- The board can change items when started with `--allow write`: Start, Block,
  Unblock, Done, Cancel and Edit in the item detail, drag and drop of a card
  to another column, and New item, each previewed before it applies. Its data
  calls are `POST /api/op/<name>` with the tool's arguments, checked for the
  token header, the board's own Origin, JSON and size before anything runs.
- The board has Next, Urgent, Ready to start and Doctor views, asked of tadu
  itself; category, type, milestone and overdue filters; a Done in the last
  choice that reloads the window; and a task's category, type, milestone,
  `defer_until` and `started`, with its relations both ways, in the detail.
- The board's scope holds any mix of companies, projects and repositories,
  chosen in one Scope tree with search, counts, ticks (a ticked company holds
  its projects and repositories, later ones included), half-ticked parents and
  Only; the address keeps them (`#place=company:acme&place=repository:shop`).
- The board's filters are rules added from a + Filter menu (F): quick filters
  (Assigned to me, Waiting on me, Overdue, Unassigned, No priority) and the
  properties the items in view have, each value with its count, several values
  per rule, matched as *is any of*, *is not* or *is empty*. Each rule is a chip
  that edits or removes it. The search box turns typed filters
  (`assignee:ana`, `-label:x`, `is:overdue`...) into chips. The Changes view
  and an item's History use the same menu and chips, with a day-range button.
- `--repository KEY` on every command reads only that repository, or names the
  one a change is made to; writing commands take `--workspace` too.
- `mark` and `claim` work on both formats, and `mark`, `claim` and `close` take
  an item's key with `--id` (its ID, a task id prefix, or the `k-` key) on both.
- `similar --json`; `show --history --json` says whether the clone is
  `shallow`.

- Accessibility of the board: the page has one main landmark, the portfolio
  table's cells have their table roles and its list rows are list items, the
  Changes view's headings follow the page's, and the muted text colour meets
  WCAG AA contrast. axe-core finds nothing on any view, the detail, the
  filters, the scope picker or the change dialog.

- Development checks on Node.js (`package.json`, `npm ci`): jscpd looks for copied code in the
  whole repository and finds none; axe-core audits every state of the board page in jsdom
  (`pytest -m browser`); and a test keeps every text colour at WCAG AA contrast in both themes.

### Changed

- `tadu mcp` serves only the reading tools unless started with
  `--allow write` (0.2.0, not yet published, offered `add`, `mark` and `close`
  always).
- MCP tool arguments are named as the command options, and other common names
  are accepted too: `notes` for `note`, `assignee` for `assignees`, `key` for
  `id` (and `id` for `show`'s `key`), `as` or `person` for `claim`'s `who`, a
  plural such as `fields` or `links` for its list. One text given for a list
  is a list of it.
- `add`, `mark` and `close` refuse an option only the other backlog format
  takes (`--kind` on a task backlog, `--type` on `TODO.md`...) instead of
  dropping it in silence.
- `add` and `mark` take `--assignee` and `--label` as repeatable options that
  also comma-separate, on both formats; `--assignees` and `--labels` are the
  same options. `mark --estimate` must be a whole number.
- `mark` and `close` need `--id` or `--match`.
- `tadu doctor` without arguments checks `.`; `doctor --workspace` also checks
  the files of every repository, and no longer takes paths beside it. `sync`
  defaults to `.` like the others.
- The board's `/api/history` and `/api/changes` are replaced by calls of
  `show` and `changes`; `/api/cards` takes `?done_days=N`.
- `tadu changes` (and the board's Changes view) says, for a changed item, how
  many lines of each field the commit added and removed (`notes: 1 added,
  1 removed`), so an edit of notes no longer shows as a change of nothing.
- The board draws a task's words under their titles (blocker, notes, done
  when, result, evidence, links, files...) instead of its raw JSON, which
  stays folded under Task file.
- The board's History section offers fields changed after the item was
  created (not every field the creation set) and marks uncommitted changes;
  a field reads `done when`, not `done_when`.
- `tadu --help` lists the commands as reading, writing, setting up, then
  serving.
- The board's three scope pickers (company, project, repository) and the
  Scope & filters popover are replaced by the Scope tree, the Filter menu and a
  Display popover (grouping, order, the done window, empty columns and
  cancelled items). Saved views, starred and recent scopes and links from
  before keep working: one place becomes a scope of one, and a saved filter
  its rules (an organization or role saved alone is dropped).

### Documentation

- The README is now an overview: what tadu is, install, a quick start, how the
  files work, the commands at a glance, short guides and how to develop tadu.
  The full reference moved to `docs/`: `commands.md` (every command and
  option), `doctor.md` (checks, pre-commit and CI, finding codes), `agents.md`
  (rule block, MCP, Claude Code hook, skills) and `workspace-and-board.md`.
- The docs name `--root` of `set` and `claim`, and `file` as a `list --sort`
  order.

### Fixed

- A change the board or an MCP call made to a `TODO.md` backlog that `tadu doctor` then found
  errors in (exit 1, after writing) was shown as refused, and as a tool error: trying again
  made it twice. It is now done, with doctor's report; doctor's own exit 1 is no tool error
  either.
- A word after `--` that starts with `-` (`tadu set -- ID -x=1`, or a tool call's value) was
  refused as an unknown option.
- The board's Changes view read one day fewer than `tadu changes` for the same "last 14 days";
  its day ranges now count as the command and `--done-days` do.
- A Unicode digit such as `²` in a `Content-Length`, a `done_days`, an `Estimate:` or
  `estimate=` value, or an archive folder's name stopped the command (or the board's request)
  with a traceback; it now reads as no number.
- A command that failed unexpectedly under `tadu mcp` or the board stopped the server; the
  call now exits 70 with the traceback as its errors.
- The board's Edit dialog dropped a field emptied by hand without a word (`tadu mark` cannot
  remove a field): it now says so and changes nothing.
- In the board's Filter menu and scope tree, Tab closed the popup; it now reaches the ways of
  matching, Remove filter and Clear, and the popup closes when the focus leaves it.
- The board offered New item and drag and drop for a workspace repository with no checkout on
  this machine.
- A typed filter named after a JavaScript object property (`constructor:x`, `is:toString`)
  broke the search box.
- The board's calls failed in a browser with `403`: with `Referrer-Policy: no-referrer` a
  browser sends `Origin: null`, and some send no `Origin` at all on a call to the page's own
  server. The board now sends `Referrer-Policy: same-origin` and checks `Origin` and
  `Sec-Fetch-Site` when they are given. A Chromium test drives the page to catch such breaks.
- The board's layout: New item sits in the page head, so the toolbar fits on one line and
  the phone page no longer scrolls sideways; five columns fit a 1440 px screen; the change
  dialog dims the page behind it, gives whole lines to notes and evidence, shows only the
  fields of the chosen repository's format and no command-line hints; a task's detail leaves
  out Kind, Check on and Not before; the views drawn from a call list their rows like the
  other lists; the filters popover scrolls; summary chips never clip their count. Five board
  columns and the toolbar fit on one line from 1280 px; below 1100 px the summary chips wrap
  instead of scrolling out of sight.
- A row of the board's Changes view could be opened only with the mouse; its title is now a
  button.
- Board cards and list rows name a task by its id (`t-55161023`) instead of a file path cut
  off mid-id, so its due date stays in view; a phone card keeps its facts on one line and has
  room for a two-line title, which overlapped them.
- Commands take options between their positionals: `tadu show KEY --history ROOT` reads ROOT
  instead of refusing it.
- `tadu mark` on a task backlog failed with "TODO.md: missing"; it now changes
  the task.
- `tadu migrate` kept a field line followed directly by `- Result:` or
  `- Evidence:` bullets, as `tadu close` writes an entry whose last line is a
  field, as a note: a closed item's `ID:` was lost and its task got a new id.

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
- `tadu migrate` keeps the prose between a `##` heading and its first item: the
  first item of the section carries it in its notes instead of dropping it.
