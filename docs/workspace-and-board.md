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
- [A board for a team: sign in with GitHub](#a-board-for-a-team-sign-in-with-github)
- [Config files](#config-files)

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
- For a [team board](#a-board-for-a-team-sign-in-with-github), a `[[person]]` takes the GitHub
  login they sign in with (`github = "octocat"`), so that they are `me` when they do; a
  `[[repository]]` needs a `remote` on `github.com`, and may carry its GitHub repository id as
  `github_id`, so a private repository renamed away and replaced by another under its old name is
  hidden from everyone.

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
on every request and on Reload. While it is visible, the page checks every 30 seconds that the
board still answers to its token: when the board stops, it clears itself until the board is back,
then reloads; after a restart, whose token is new, it clears itself and asks for the new URL.

Its options (`--host`, `--port`, `--done-days`, `--allow` and, for a team, `--auth`, `--public-url`,
`--sign-in-limit`, `--idle-timeout` and `--proxy-hops`) are in the
[command reference](commands.md#board), and each can be set in a [config file](#config-files); Done from the last, under Display, changes the Done
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

## A board for a team: sign in with GitHub

With `--auth github`, the board serves a team: people sign in with their GitHub account, and each
of them sees only the items of the workspace repositories they can read on GitHub.
[team-board.md](team-board.md) is the full guide: registering the GitHub App, preparing the
workspace, running behind https, the ids file, how much GitHub is asked, the security model, the
limits and troubleshooting.

```bash
export TADU_GITHUB_CLIENT_ID=Iv23liAbCdEf0123
export TADU_GITHUB_CLIENT_SECRET=...   # never on the command line
tadu board --workspace . --auth github --port 8123 --public-url https://board.example.com
```

- Register a GitHub App whose callback URL is the public URL plus `/auth/callback` and which needs
  no permission beyond the default read-only Metadata, and install it on the organizations that
  own the repositories. An OAuth App works too, but must ask for the `repo` scope, which allows
  writing.
- Every workspace repository needs a `remote` on `github.com`; one without is shown to nobody, and
  `board` says so when it starts. Give each `[[person]]` their login (`github = "octocat"`) so
  that they are `me` when they sign in.
- Serve it behind a reverse proxy that terminates https, on a subdomain
  (`https://tadu.example.com`), a domain of its own, or a subfolder of another site
  (`https://example.com/tadu`, with the proxy keeping or taking away the `/tadu` prefix).
  `--public-url` is the address people open; it is only valid with `--auth github`. Prefer a
  subdomain or own domain: in a subfolder, the site's other pages share the board's origin. The
  guide has Caddy and nginx configurations for each.

What it guarantees:

- Access is checked with each person's own GitHub token, from their repository list with ETags,
  so a 100-repository workspace costs one or two requests per person every 5 minutes, nearly all
  of them free `304`s. Repositories they cannot read are not even scanned for them, and nothing
  about them reaches their browser: not items, keys, projects, organizations, saved views or scan
  problems.
- Each workspace repository is tied to its GitHub repository id, learned into
  `tadu-workspace.github-ids.json` beside the workspace file (or given as `github_id` on the
  `[[repository]]`), so a private repository renamed away and replaced by another under its old
  name is hidden from everyone, also after a restart.
- When in doubt it hides: a repository that cannot be checked (rate limit, GitHub down, SAML) or
  whose identity cannot be confirmed is hidden, with a notice that names nothing, and the
  operator gets the details on standard error.
- Starting and finishing a sign-in is rate limited per address: 10 a minute each by default, as
  GitLab limits its sign-in paths, with `429` and `Retry-After` beyond it; `--sign-in-limit`
  (such as `5/minute;50/hour`, or `off`) changes it, and `--proxy-hops 1` reads the client's
  address from a trusted reverse proxy.
- Sessions last while they are used: they end after 14 days of inactivity, or the
  `--idle-timeout` given, such as `8h`; clicking, typing or scrolling on an open page counts as
  activity, and the page warns 5 minutes before the end. GitHub tokens are renewed in the
  background, and sessions survive restarts: they are saved in `tadu-workspace.sessions.json`
  (keep it out of git), each sealed with `cryptography`'s Fernet under a key only the person's
  cookie gives, so the file signs nobody in and holds no usable token. Cookies are `HttpOnly`,
  `SameSite=Lax`, and `Secure` and `__Host-` prefixed behind https; signing out ends the session,
  and a token GitHub refuses ends it within 5 minutes.
- Signing in uses PKCE and GitHub's account picker (so a shared computer does not sign the next
  person in as the last), signing out has GitHub revoke the token, and only the board's own page
  may load its data, check the session or sign out: pages of other sites, and of other origins of
  the same site, are refused.
- Besides the page's calls, a team board writes only `tadu-workspace.github-ids.json` and
  `tadu-workspace.sessions.json`, and a POST signs out. It never writes a checkout: a change made
  with `--allow write` becomes a pull request (or, for someone who cannot push, an issue) opened
  with the person's own token; see the guide's "Changes are proposals".

Its limits, in short: github.com only (no GitHub Enterprise Server), one process per workspace,
access changes on GitHub take effect within 5 minutes, items are what the server's checkouts hold
(pull them on a schedule), anyone with a GitHub account can sign in and sees the workspace's public
repositories, and a board that first sees a repository after its name was taken over cannot tell
unless `github_id` is set. The guide lists them all.

## Config files

Options you would give every time can live in a file instead; a flag on the command line always
wins. The user's config file is `config.toml` in tadu's config directory (`~/.config/tadu/config.toml`
on Linux, or under `$XDG_CONFIG_HOME`; `~/Library/Application Support/tadu/config.toml` on macOS;
`%LOCALAPPDATA%\tadu\config.toml` on Windows), or the file `$TADU_CONFIG` or `--config FILE` names:

```toml
# ~/.config/tadu/config.toml
version = 1

[defaults]              # every command that has the option
workspace = "~/work/acme-workspace"
json = false

[list]
sort = "priority"
limit = 30
view = "my-urgent"      # a [[view]] of the workspace: filters belong there

[board]
port = 8123
```

A workspace's `tadu-workspace.local.toml` takes the same tables, for the commands run on that
workspace, and wins over the user's file. That is where a server keeps its board:

```toml
# /srv/team-workspace/tadu-workspace.local.toml
version = 1

[paths]
shop = "/srv/checkouts/shop"

[board]
auth = "github"
public_url = "https://tadu.example.com"
port = 8123
proxy_hops = 1
```

```bash
tadu board --workspace /srv/team-workspace                 # the settings above
tadu board --workspace /srv/team-workspace --port 9000     # one of them overridden
```

- **Order:** the command line, then the workspace's local file (`[command]`, then `[defaults]`),
  then the user's file (the same), then the built-in default. The workspace is `--workspace`, else
  the user's file's.
- **A repository keeps to itself.** A command that reads repositories (`list`, `show`, `next`,
  `inbox`, `urgent`, `ready`, `similar`, `feed`, `mcp`) ignores a workspace from a file when the
  command line names repository paths, or when it runs in a repository with a backlog (a
  `TODO.md` or `todo/tadu.json`), which is then its default path; a `view` from a file goes with
  it. So `tadu list .`, and an agent running `tadu next` in one repository, see that repository
  only, never the workspace's other items; `--workspace` still reaches the workspace from
  anywhere. `board` and `doctor`, which have no default path, use the configured workspace
  wherever they run.
- **Keys** are the long flags with `_` for `-` (`public_url` for `--public-url`), checked as the
  flag is: `port = 8123` or `"8123"`, `json = true`. `--no-json` turns off a `json = true`. A
  `workspace` in the user's file is relative to that file and may start with `~`; the local file
  cannot name one.
- **What a file can set:** where a command reads and how it prints or serves, never what one call
  acts on.

  | Table | Keys |
  | --- | --- |
  | `[list]` | `workspace`, `done_days`, `view`, `json`, `sort`, `limit` |
  | `[show]` | `workspace`, `done_days`, `json` |
  | `[ready]` | `workspace`, `json`, `limit` |
  | `[next]`, `[inbox]` | `workspace`, `json` |
  | `[urgent]` | `workspace`, `json`, `days` |
  | `[similar]` | `workspace`, `limit` |
  | `[feed]` | `workspace`, `done_days` |
  | `[doctor]` | `workspace`, `json` |
  | `[board]` | `workspace`, `host`, `port`, `done_days`, `auth`, `public_url`, `sign_in_limit`, `proxy_hops`, `idle_timeout` |
  | `[mcp]` | `workspace` |
  | `[init]` | `file`, `format` |
  | `[sync]` | `file` |
  | `[defaults]` | any key above, for every command that has it |

  Item selectors and contents (`--match`, `--id`, `--title`, `--evidence`, the `list` filters and
  the like) and `--write` stay on the command line, so a file can never make a command pick
  another item or write without being asked; a filter set you want by default is a saved
  `[[view]]`, named by `[list] view`. Who acts is not a setting either: `me` in the local file and
  `$TADU_ACTOR` say it. The GitHub client secret is read from the environment only.
- **The board's GitHub settings follow its `auth`.** `public_url`, `sign_in_limit`, `proxy_hops`
  and `idle_timeout` need `auth = "github"`; a file that sets them without it stops the board,
  naming the file. `--auth token` on the command line overrides a file's team board as a whole and
  drops the file's GitHub settings with it, so `tadu board --workspace /srv/team-workspace --auth
  token` is a private look at a server's workspace.
- **`--no-config`** (before or after the command) reads neither file's tables, for a script that
  must not depend on anyone's settings. MCP tool calls run that way, so a tool does what its
  description says.
- A file that cannot be used (unknown table or key, a value the flag would refuse, a missing file
  named by `--config` or `$TADU_CONFIG`) stops the command with exit `2`, naming the file, the
  table and the key. A value is checked when a command that uses it runs.

The design brief of the page is in [ui-brief.md](ui-brief.md).
