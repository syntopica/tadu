# tadu board: a portfolio board over repository backlogs

Status: draft for owner review, 2026-11-04. Nothing is built yet.

## Intent

tadu keeps one backlog per repository. Someone who runs many repositories, for
themselves or for an agency with several clients, has no single place to see
what is open across all of them, who holds it, what matters most, and what is
blocked. Issue trackers such as Jira or Linear answer that by moving the tasks
into their own database. tadu board answers it while the tasks stay in the
repositories: each `TODO.md` stays the only copy, and the board, the JSON
output and later the agent tools are views over those files.

It is a public part of tadu that anyone can install. One person may run several
independent workspaces: a personal one, one per agency or company, and more
later. Each workspace sees only the repositories registered in it.

## Goals

- Collect the open items of every registered repository and show them as cards
  on a kanban board in a browser.
- Filter by repository, project, client, company or agency, assignee, priority
  and state. Several repositories can be grouped into one project.
- Give items an optional priority, assignees, due date and labels, and give
  them a stable ID.
- Agents can use everything the board shows through a documented JSON CLI, with
  an MCP adapter later.
- Describe who each project is for with a configurable relationship model, for
  example "project X, client Y, delivered by agency Z", where the same
  organization can be the client in one engagement and the agency in another.
- Keep exactly one source of truth for every fact. Nothing gets copied between
  repositories, the workspace and the board.

## Non-goals

- A hosted or cloud collaboration service, accounts, or billing.
- Custom workflow designers, arbitrary custom fields, mandatory estimates,
  velocity or burndown metrics, sprints or cycles (they can come back once
  weekly planning has proved useful), chat or comments inside the board.
- Replacing Git as the means of syncing between machines and people.

## Anti-goals

These would make the board a failure even if it worked:

- A second database becoming authoritative for any task field. If a card and
  its `TODO.md` line ever disagree, the file is right and the board is broken.
- Rewriting backlog files the board did not need to touch, or reformatting the
  heterogeneous backlogs already out there into one shape.
- Leaking one workspace's repositories, people or task text into another, or
  into anything outside the machine.
- Breaking any existing tadu v1 repository, `tadu doctor` result or
  `tadu close` behaviour.

## Constraints

- tadu has no runtime dependencies and requires Python 3.12 or newer. The board
  keeps that: standard library only, including the web server.
- Repository conventions in `AGENTS.md` apply: one top-level unit per source
  file, one test file per module, and the full quality gate with 100% branch
  coverage.
- The format extension is additive to v1. A file without the new fields is
  exactly as valid as today.
- Backlogs in the wild differ a lot: from about ten lines to over a thousand,
  with nested sub-steps, long continuation histories and legacy sections. The
  scanner reads top-level items tolerantly and reports what it cannot parse,
  without guessing.
- This repository is public. The examples, fixtures and docs name no real
  client, person or private repository.

## Sources of truth

| Fact | Lives in |
|---|---|
| Item text, state, ID, priority, assignees, due date, labels | the owning repository's `TODO.md` |
| Closed items and their evidence | the owning repository's `TODO_LOG.md` |
| Which repositories a workspace covers, the projects that group them, the organizations and their roles, the people | the workspace file (below) |
| Where each repository is checked out on this machine | an untracked local file next to the workspace file |
| Board ordering, scan results, caches | derived and disposable, never committed |

## The format extension

Optional `Key: value` fields, each written as its own continuation paragraph of
a top-level item. That is the same shape v1 already uses for `Done when:` and
`Depends on:`. They render visibly, survive Prettier without the nested-list
loop the spec warns about, and `tadu close` already carries continuation lines
into the log.

```markdown
- [ ] **Billing:** Reject duplicate webhook deliveries.

  ID: t-55161023-f3a9-43a3-94df-589ca752fa13

  Priority: high

  Assignees: ana, bot

  Due: 2026-11-20

  Labels: billing, reliability

  Queue: ready
```

- `ID:` is `t-` followed by a random UUID4, generated wherever the item is
  created. No server, counter or machine identity is involved, so two machines
  cannot collide. An ID never changes, including on close and when a backlog
  moves to another repository. A copied item gets a new ID.
- `Priority:` is one of `urgent`, `high`, `normal`, `low`. Leaving it out means
  unprioritized, not normal.
- `Assignees:` is a comma-separated list of person IDs from the workspace file.
  It is never an email or a display name, so that a public repository does not
  carry contact details.
- `Due:` is a calendar date, `YYYY-MM-DD`.
- `Labels:` is a comma-separated list of lowercase slugs.
- `Queue:` is `backlog` or `ready`, defaulting to `backlog`. It applies only to
  `[ ]` items.
- `Estimate:` is reserved for a positive number of minutes. It is parsed but not
  shown in the first version.
- Field names are matched exactly and only in the item's own continuation
  paragraphs, never inside fences or nested sub-steps. Unknown `Key: value`
  paragraphs are kept untouched. A recognized field that appears twice, or an
  invalid value, is a `doctor` warning (never an error), so adopting the fields
  cannot fail an existing gate.

The spec gains a section describing these fields, the `doctor` warning codes
and the `list --json` schema. The format version stays v1.

## Board columns

| tadu state | Column |
|---|---|
| `[ ]` without `Queue: ready` | Backlog |
| `[ ]` with `Queue: ready` | Ready |
| `[~]` | In progress / unverified |
| `[!]` | Blocked |
| `[x]` from `TODO_LOG.md`, recent window | Done |
| `[-]` from `TODO_LOG.md` | Cancelled, hidden by default |

There is no new checkbox state. "Needs review" is a label. "Waiting on me" is a
filter: assigned to me and blocked.

## The workspace

A workspace is a directory, normally a small Git repository of its own, that
holds one `tadu-workspace.toml`. It is read with the standard library's
`tomllib` and starts with `version = 1`; the spec gains a section that documents
both workspace files and is versioned like the rest of the format. It lists:

- the repositories, each with a short key, its canonical remote URL and an
  optional backlog subdirectory (default: the repository root, so a monorepo
  can register a nested `TODO.md` as its own entry);
- the projects, each grouping one or more repository keys. Within one workspace
  a repository entry belongs to at most one project, so every card has one
  project or none;
- the organizations, each with an ID and a display name;
- for each project, its organizations by role (`client`, `agency`, `company`,
  or any other role string), each role holding one or more organization IDs.
  That is how one organization can be the client of one project and the agency
  of another. In `list --json` a card carries one `project` and a list of
  `{role, org}` pairs; `--org` matches any pair and `--role` narrows it;
- the people, each with an ID, a display name and, optionally, the organization
  they belong to.

The checkout path of each repository on this machine goes in an untracked
`tadu-workspace.local.toml` beside it, so that two machines and two people can
share one workspace file. The local file also names who "me" is (a person ID)
for the "Waiting on me" filter, and an optional editor URL template such as
`vscode://file/{path}:{line}`. A repository can be registered in several
workspaces at once; its tasks are still read from its one `TODO.md`.

A workspace may link to outside pages (a wiki page for a client, for example)
by URL, but it does not copy their content.

## Interfaces in the first version (read-only)

- `tadu list --json` prints one JSON object per item from every repository in
  the workspace, or from the repository roots given as arguments when no
  workspace is named. Each object carries its source path and line span, state,
  column and parsed fields, plus the project and organizations it resolves to.
  It filters by `--project`, `--org`, `--role`, `--assignee`, `--state`,
  `--priority`, `--label` and `--due-before`. An item without an `ID:` gets a
  key derived from its repository, file and first line, flagged as unstable.
- `tadu show <id> --json` prints one item with its full text.
- `tadu board --workspace <dir>` starts a local web server, bound to
  `127.0.0.1` by default, serving one static page and the same JSON. One
  process serves one workspace; for two workspaces, run two. The page filters
  and groups without a build step. Each card shows its `path:line` to copy, a
  link through the editor URL template when the local file sets one, and a link
  to the line on the remote when the remote is a known forge; the server itself
  never launches anything. Item text is escaped, never rendered as raw HTML.
  The server prints a URL carrying a random per-run token, requires it on every
  request including the JSON, rejects a `Host` header other than the bound
  address, and sends no CORS headers, so another local page or process cannot
  read the board.
- The Done column shows entries dated within the last 14 days (`--done-days`
  changes it). Only entries on or after the log's `tadu:log v1 since` marker
  are parsed; without a marker, only dated top-level entries are read, and
  anything the scanner cannot parse is reported rather than guessed.
- `tadu doctor` warns about malformed new fields, about assignees missing from
  the workspace when one is given, and about IDs repeated across the workspace's
  repositories. The Claude Code hook keeps reporting errors only, so these
  warnings do not reach an agent until `doctor` is run.

The first version writes nothing at all: no backlog, no workspace, no index on
disk. It rescans the files on each request, keeping cached results only while a
file's modification time and size are unchanged.

## Later, in order

1. `tadu id --write` assigns IDs to items that lack them, and `tadu close --id`
   closes by ID.
2. One mutation function shared by the CLI, the board and MCP. It takes an item
   ID, the change, and the hash of the file as the caller last saw it. It locks
   the repository, rereads the file and refuses if the file changed, patches
   only that item's span, runs `doctor`, writes, commits only the backlog paths
   and pushes according to the repository's own policy. It refuses to run on a
   dirty worktree or with staged changes, and it never stashes, resets or
   force-pushes. The board shows local, committed and pushed status separately.
   Closing needs a recoverable journal, because it writes two files.
3. An MCP adapter over the same functions, as an optional extra so that core
   keeps no dependencies.
4. Cross-repository `Depends on:` by ID, a "recently done" feed from the logs,
   item history from `git log`, ageing of blocked items, saved views.

## Pending owner decision

Who besides the owner opens a company workspace's board (for example an
agency's), and whether those people only look or also move and edit cards. That
answer decides whether the board stays a local tool or also runs as a shared
server with authentication, and how edits from people who do not use agents
reach the repositories. The read-only first version does not depend on it, and
neither does anything above step 2 of "Later".

## Calls made in this draft, not yet confirmed by the owner

- A workspace is a directory with a TOML file, normally its own Git repository,
  rather than a section of an existing wiki or tracker.
- The web server uses the standard library and lives in core tadu, instead of a
  separate package with dependencies. Only MCP becomes an optional extra.
- No SQLite index in the first version. About a hundred backlog files are cheap
  to rescan, so an index waits until a measurement shows a need.
- One workspace per board process.
- Field validation produces warnings only.
- Assignees are workspace person IDs, and agents (for example `bot`) are people
  in that list like anyone else.
- A repository entry belongs to at most one project per workspace; a project
  holds its organizations by role, several per role allowed.
- Backlogs in a subdirectory are registered as their own repository entry.
- Cards link out by `path:line`, an optional editor URL template and the remote
  forge; the server never launches an editor.
- The server requires a per-run token and checks `Host`, even on localhost.
- Done shows 14 days by default and parses only checked log entries.
- The Claude Code hook stays errors-only.

## Left to the builder

The page's visual design and layout; the exact JSON field names, within the
contents listed above; the `doctor` warning codes; the module split, within the
one-unit-per-file rule; how the derived key for items without an ID is
computed; the caching details; and the test fixtures, provided they name no real
organization or person.

## Outside this repository

An existing private control plane keeps its own ticket table, and it already
claims `TODO.md` items. Once `tadu list --json` exists, that system should read
from it instead of holding a second copy of task fields. That change belongs to
that system's repository and is not part of this design.
