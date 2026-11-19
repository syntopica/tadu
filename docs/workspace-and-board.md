# Workspaces and the board

A workspace reads several repositories as one backlog: every command, and `mcp`, takes
`--workspace DIR`, and `tadu board` serves it as a kanban page, read-only unless started to allow
changes.

- [A workspace](#a-workspace)
- [Saved views](#saved-views)
- [The board](#the-board)
- [Changing items on the board](#changing-items-on-the-board)
- [Who may change what](#who-may-change-what)
- [Who may read the board](#who-may-read-the-board)

## A workspace

A workspace is a directory with a `tadu-workspace.toml` shared by the people who use it, and an
untracked `tadu-workspace.local.toml` that says where each repository is checked out on this
machine. The smallest useful one:

```toml
# tadu-workspace.toml
version = 1

[[repository]]
key = "shop"

[[person]]
id = "ana"
name = "Ana"
```

```toml
# tadu-workspace.local.toml
version = 1
me = "ana"

[paths]
shop = "../shop"
```

- Paths in `[paths]` are resolved: `~` expands and `..` is normalised.
- Projects, organizations with roles such as client and agency, repository remotes and an editor
  link template are optional. The [format 1 spec](../spec/todo-format-v1.md#workspaces) has the
  full shape of both files.
- `me` names the person `next` and `inbox` act for, and the board's My work.

Then check it and open the board:

```bash
tadu doctor --workspace .
tadu board --workspace .
```

`doctor --workspace` reports unknown assignees (`W001`), IDs shared between repositories
(`W002`), repositories that could not be scanned (`W003`) and an invalid workspace (`W004`).

## Saved views

A `[[view]]` table saves a named filter set, with the `list` filter names (`due_before` and
`check_before` as TOML dates):

```toml
[[view]]
name = "my-urgent"
assignee = "ana"
priority = "urgent"
```

```bash
tadu list --workspace . --view my-urgent
```

Filter flags given beside `--view` replace the view's criterion.

## The board

```bash
tadu board --workspace .
```

`board` prints a URL such as `http://127.0.0.1:41873/?token=...`; open it in a browser from 2024
or later (the page's light and dark colours use CSS `light-dark()`). The files are rescanned
on every request and on Reload.

Its options (`--host`, `--port`, `--done-days` and `--allow`) are in the
[command reference](commands.md#board); Done from the last, under Display, changes the Done
window on the page, and `--allow` is explained in [Changing items on the board](#changing-items-on-the-board).

Without `--port` the board listens on a port derived from the workspace path (40000 to 49999), so
the URL, and the saved views the browser keeps for it, stay the same across restarts; when that
port is busy it takes any free port and says so on standard error. Port 80 also accepts the bare
host, since browsers omit it.

### Views

The sidebar has eleven views:

| View | Shows |
| ---- | ----- |
| My work | open items assigned to `me` |
| All work | every open item |
| Next | what [`tadu next`](commands.md#next-inbox-urgent) lists for `me`: tasks an agent can do alone, most pressing first |
| Urgent | what `tadu urgent` lists, under who acts (Do, Decide, Chase, Check, Blocked) |
| Ready to start | what [`tadu ready`](commands.md#ready) lists: open items nothing blocks or defers |
| Blocked | all blocked items, those blocked for me, and unassigned ones |
| Portfolio | counts per company, project and repository |
| Done | items closed in the window, by day |
| Changes | what changed in a range of days, as [`tadu changes`](commands.md#changes) prints it (below) |
| Doctor | what [`tadu doctor --workspace`](commands.md#doctor) finds, errors first |
| Board | a column per state, at most 30 cards each, with a link to the full list |

Next, Urgent, Ready to start and Doctor ask tadu itself, by the same call as the command of that
name, each time the board loads; the scope at the top narrows their items.

### Scope

Every view, and every count on the page, shows the places chosen with the Scope button at the
top: any mix of companies, projects and repositories, or everything when none is chosen.

- The Scope button opens a tree of companies, their projects and their repositories, each with
  its count of open items, under the starred and recent scopes. Ticking a row adds it; a
  company or project shows ticked, or half-ticked when only some of what it holds is, and
  ticking one replaces whatever inside it was ticked. Unticking a repository of a ticked
  company keeps the company's other projects and repositories. Only, beside a row, keeps that
  place alone.
- A ticked company holds its projects and repositories as they are when the page reads the
  workspace, so a project added to it later is in the scope without being ticked again; the
  same goes for a ticked project's repositories.
- Typing narrows the tree to the rows that match, with the rows around them. The arrows move,
  Right and Left unfold and fold, Enter keeps the active row alone and closes, Shift+Enter ticks
  or unticks it and stays. Clear goes back to everything.
- A project's company is the organization it lists under the role `company`. Other roles, such
  as `client`, are relations: they show as badges ("Client: Automate Texas") and never as
  ownership. A project with two companies sits under both, ticked under both.
- Projects that name no company sit under No company, and repositories in no project under No
  project. A workspace without projects lists its repositories alone.
- The Companies section of the sidebar is a shortcut: a company's or project's name shows it
  alone.
- The scope stays as you switch views, is kept per workspace in the browser, and is part of the
  address (`#place=company:acme&place=repository:shop&view=board`; links made before scopes
  could hold several places, `#company=...&project=...`, still open), so a copied URL reopens
  the same view and scope. Star a scope to keep it in the sidebar; the last five scopes used are
  listed under Recent.

Portfolio counts the scope as a tree, Company > Project > Repository, where each project appears
once under the company that owns it and every row sums distinct repositories; Group: Client lists
the projects under their client organizations instead. A row's name opens its items in its scope,
its blocked count the Blocked view of them.

### Lists and details

- Every list and the board have a toolbar: search, + Filter, Display and the layout.
- + Filter (or F) opens a menu, searchable as you type, of quick filters (Assigned to me,
  Waiting on me, which shows what `tadu inbox` lists for `me`, Overdue, Unassigned, No
  priority) and of the properties the items in view have: state, assignee, priority, label, due
  date, kind, category, type, milestone and organization. A property opens its values, each
  with how many items in view hold it; tick as many as you like. A rule matches an item with
  any of its values (*is any of*), with none of them (*is not*), or with no value at all (*is
  empty*, such as unassigned). The due date offers Overdue, Today, Next 7 days and a day to be
  due before.
- Each rule shows as a chip under the toolbar ("Assignee · is any of · ana, bo"): a click edits
  it, its cross removes it; values of one rule are alternatives, and every rule must hold.
  Clear all removes them, Save view names the list in the sidebar. The row shows only while a
  filter is on; in the empty search field, Backspace removes the last rule.
- The search box also takes filters typed as the command options name them, turned into chips
  as soon as a word is complete: `assignee:ana`, `priority:urgent,high`, `-label:security`
  (*is not*), `assignee:none` (*is empty*), `state:in-progress` (or `column:`, as `list
  --column` names it), `due:overdue`, `due:2026-12-01` or `due-before:2026-12-01` (due before
  that day), `is:mine`, `is:overdue`, `is:unassigned`, `is:waiting`. A word that names nothing
  stays in the search. Overdue, here as in the Filter menu, is an open item due before today.
- Display holds what is not a filter: the grouping, the order, how many days of closed items
  the page reads (Done from the last), whether the board shows its empty columns and whether
  cancelled items show.
- A decision, waiting or later item carries a badge saying so, and a `Check on:` day shows beside
  the due date. Group: Kind splits any list into tasks, decisions, waiting on others and later.
- Lists draw only the rows on screen, so a workspace of thousands of items stays fast.
- Clicking an item opens its detail: company, project, repository and relations, location, ID,
  fields (and a task's category, type, milestone, `defer_until` and `started`), its words, its
  relations to other items both ways (parent and children, blocked by and blocks, related,
  duplicates; one on the board opens on click), parse warnings, and links to the editor and the
  forge. A Markdown item's words are its text as written; a task's are its fields drawn under
  their titles (blocker, to unblock, notes, done when, result, evidence, resolution, links and
  files; `**bold**` and `` `code` `` drawn, an `https` link followed), and its file as it is on
  disk stays folded under Task file.
- The detail's History section, folded, shows the changes git recorded to the item, the same
  entries as [`tadu show --history`](commands.md#history): each commit's subject, short id,
  author and time, the fields that changed and the lines added or removed, newest first. It is
  read from git only when it is opened, and again after Reload while it stays open; a repository
  outside git says so there; uncommitted changes come first, marked in the colour of work in
  progress. Its toolbar is the Changes view's: the days (any time, the last 7, 30 or 90, or a
  range) and + Filter by author and by field changed (the entry that created the item aside),
  each with its count; the fields match as in
  [`show --history`](commands.md#filtering-the-history). It narrows what was read without
  reading git again, and stays with the item across a Reload.
- Saved views (with their scope), starred and recent scopes and the light or dark theme are kept
  in the browser's `localStorage`. Under 720 px the page becomes a list with a bottom bar, and the
  portfolio one card per company.

### Changes

The Changes view shows what changed across the workspace in a range of days, the last 14 by
default: the same changes as [`tadu changes`](commands.md#changes), grouped by kind (closed,
reopened, started, blocked, created, changed...) with how many and who made them, newest first.

- The days button offers the last 7, 14 or 30 days, this month, last month, or a range (From
  and To, then Apply); git is read only for days not read since the board last loaded, and
  again after Reload.
- + Filter narrows what was read, without reading git again, by kind of change, author and field
  changed, each value with its count, as the lists' Filter menu does; each rule is a chip, and
  Clear filters removes them. Nothing else takes room until a filter is used. The scope at the
  top applies as in every view.
- A changed item's row says what changed, as `tadu changes` does: its fields, and the lines
  added and removed per field.
- A row whose item is on the board opens its detail; its title is a button, so the keyboard
  reaches it too.
- Repositories git cannot read are listed above the changes.

### Keys

| Key | Does |
| --- | ---- |
| `/`, Cmd/Ctrl-K | search |
| F | the Filter menu (type to find; Enter chooses, Esc steps back, Shift+Tab reaches *is any of*, *is not* and *is empty*) |
| G then S | the scope tree (type to find; Enter keeps one place, Shift+Enter ticks) |
| J, K | move |
| Enter | open the detail |
| E | open the editor |
| Esc | close |

## Changing items on the board

By default the board only reads, and says so in the sidebar. Started with `--allow write`, it can
change items:

```bash
tadu board --workspace . --allow write
```

- The detail of an open item offers Start (`tadu claim` for `me`, else `mark --state
  in_progress`), Block… (asks what blocks it), Unblock, Done… (asks for the evidence), Cancel…
  (asks why) and Edit… (priority, assignees, labels, dates, queue, estimate, a note).
- On the Board, drag an open card to another column: Backlog and Ready set it open in that queue,
  In progress starts it, and Blocked, Done and Cancelled open the form that asks why. Empty
  columns stay shown so a card can be dropped there. Closed items do not move.
- New item, in the toolbar, adds an item to a repository the page may change, and its Preview
  lists the open items most like it, as [`tadu similar`](commands.md#similar) does.
- A form shows what tadu would write with Preview, and writes with Apply; a change without a form
  applies at once. A refusal keeps the form open with what tadu said. After a change the board
  reloads.
- Everything works from the keyboard: a card takes Enter or Space, and its detail makes every
  change a drag makes. The form is a modal dialog: the page behind it is inert, Esc closes it,
  and the focus returns to the button that opened it; what tadu said is announced, and so is
  the line saying a change was made.

Each change is the command of that name run with `--write`, through the same call
[`tadu mcp`](agents.md#mcp-server) makes: `mark`, `close`, `claim` and `add` check, lock and
refuse exactly as on the command line, and each form takes its choices from the command's own
arguments. `--allow admin` also offers `sync`, `init`, `archive`, `fmt` and `migrate` as calls, for
an agent or a script; the page itself has no button for them.

## Who may change what

Two limits apply, and the lower one wins:

- What the server was started with: `tadu board --allow` and `tadu mcp --allow`, `read` by
  default, else `write` (items) or `admin` (also whole-backlog rewrites). The board answers a
  call above it with `403`; MCP does not even list the tool.
- What each repository allows through the workspace, with `access` in `tadu-workspace.toml`:

```toml
[[repository]]
key = "client-site"
access = "read"   # read, write or admin (the default)
```

A change to such a repository exits `2` with `repository client-site allows read only`, whether
it comes from the board, from MCP serving the workspace, or from `tadu ... --workspace DIR` on the
command line; the page shows no change for its items. A repository given as a path is not
limited: the workspace is not involved.

## Who may read the board

- The server checks the `Host` header against the address and port it is bound to (bound to
  `127.0.0.1`, it also accepts `localhost:<port>`) and answers `421` otherwise, which defeats DNS
  rebinding.
- The page and its scripts and stylesheet need only that; the server serves only files directly
  inside its own `board` directory. The cards, at `GET /api/cards` (`?done_days=N` for another
  window), also need the per-run token, as an `X-Tadu-Token` header or a `?token=` parameter; a
  missing or wrong token answers `403`. The page keeps the token in `sessionStorage` and removes
  it from the address bar.
- Everything else is a call: `POST /api/op/<name>` with the tool's arguments as a JSON object,
  answered with the command's exit `code`, `output` and `errors`, as `tadu mcp` runs it over the
  workspace. An item's history is `show` with `history` and `json`; the Changes view is `changes`
  with `json`. A call must carry the token in the `X-Tadu-Token` header (never in the address),
  no `Origin` or `Sec-Fetch-Site` but the board's own (a browser may leave `Origin` out on a
  call to the page's own server), and a JSON body of at most 64 KiB; otherwise it answers `403`,
  `415`, `411` or `413`, before anything runs. Another site's page has no token, and its browser
  sends a call with a custom header or a JSON body only after a preflight the board refuses. An unknown tool answers `404`, one above `--allow`
  `403`, a body that is not a JSON object `400`; arguments that do not fit the tool's schema
  come back as exit `2`, as over MCP.
- Calls run one at a time, each as the command line runs it. Other methods answer `405` with
  `Allow: GET, POST`, and a connection that stalls for 30 seconds is dropped.
- No response carries a CORS header, so another page cannot read the data. Responses send
  `Referrer-Policy: same-origin` (no address leaves the board, and a call's `Origin` still names
  it: `no-referrer` would make browsers send `Origin: null`), `Cache-Control: no-store` and a
  Content-Security-Policy that allows only the page's own script and style.
- Item text is escaped, never rendered as HTML: only `**bold**` and `` `code` `` in titles are
  styled, built as elements holding plain text.
- A `--host` other than `127.0.0.1` or `localhost` prints a warning: the server listens on that
  address, but still serves only requests whose `Host` header is exactly `<host>:<port>`, and,
  with `--allow`, anyone who has the token may change items. `::1` is not supported. An invalid
  workspace or a port that cannot be bound exits `2`.

The design brief of the page is in [ui-brief.md](ui-brief.md).
