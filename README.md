# tadu

tadu is a backlog format for repositories that coding agents maintain, plus the tools that keep it honest.

A repository keeps its backlog in one of two formats:

- Format 1: `TODO.md` is the active backlog and `TODO_LOG.md` records closed work with its evidence ([spec/todo-format-v1.md](https://github.com/syntopica/tadu/blob/main/spec/todo-format-v1.md)).
- Format 2: one JSON file per task under `todo/`, with `todo/tadu.json` declaring the categories, types and policies ([spec/todo-format-v2.md](https://github.com/syntopica/tadu/blob/main/spec/todo-format-v2.md)). Agents query it instead of reading it, and parallel branches merge without conflicts.
- In both, `TODO_HISTORY_INDEX.jsonl` is an optional index of the conversations already reviewed.

The commands:

- `tadu init` starts the backlog in a repository that has none (`--format 2` for a task backlog).
- `tadu doctor` checks a repository against its format and never writes.
- `tadu sync` updates the marked rule block in an agent instruction file.
- `tadu add` puts one new item into the backlog, such as a decision for a person; on a task backlog it creates a task file.
- `tadu mark` sets an open item's state: blocked with its blocker named, open again, or in progress.
- `tadu close` closes one open item: into `TODO_LOG.md`, or (format 2) into `todo/closed/`.
- `tadu list` prints the items of one or more repositories, or of a workspace, as lines or JSON, with filters an agent can aim with.
- `tadu show` prints one item by its key, with the relations that point at it.
- `tadu next` lists the tasks an agent can do now without a person.
- `tadu inbox` lists what waits on a person: decisions, follow-ups and checks whose day has come, their blocked tasks.
- `tadu urgent` lists what is urgent, high priority or due soon, by who has to act.
- `tadu ready` prints what can be worked on now; `tadu similar` finds existing items like a new one.
- `tadu set` and `tadu claim` change and take tasks of a task backlog; `tadu archive`, `tadu fmt` and `tadu migrate` maintain it (see [Task backlog](#task-backlog-format-2)).
- `tadu feed` prints the recently closed items of one or more repositories, or of a workspace, as JSON.
- `tadu board` serves a read-only kanban page for a workspace, to you alone or, with GitHub sign-in, to a team.
- `tadu hook claude` is a Claude Code hook that runs `doctor` after an agent changes the backlog.
- `tadu mcp` serves `next`, `inbox`, `urgent`, `list`, `show`, `add`, `mark` and `close` as tools an agent sees without any instruction file.

Contributors need none of it: the rule block that `sync` writes into `AGENTS.md` or `CLAUDE.md` tells any agent, or any person, how to add an item and how to log closed work in a shape `doctor` accepts.

## Requirements

Python 3.12 or newer. Any Python installer brings the few libraries tadu uses along with it: `cryptography`, `requests` and `requests-oauthlib` (with `oauthlib`), Werkzeug and `limits` for the board's GitHub sign-in, `filelock` for locking a backlog on Windows, and `platformdirs` for each system's cache directory. A command imports only what it runs, so `tadu list` loads none of the sign-in libraries. [uv](https://docs.astral.sh/uv/) is only needed to work on tadu itself. Its test suite also drives the board in a real Chromium through Playwright: run `uv run playwright install chromium` once, or point `TADU_TEST_BROWSER` at a Chromium or Chrome program; without one those tests are skipped, unless `TADU_REQUIRE_BROWSER` is set, as it should be in CI.

## Install

tadu needs Python 3.12 or newer; the installer brings its libraries. Install it as a command with any Python installer:

```bash
uv tool install tadu
# or
pipx install tadu
# or, into the current Python environment
python3 -m pip install tadu
```

The development version installs from git the same way, for example `uv tool install git+https://github.com/syntopica/tadu`.

```bash
tadu --version
```

```text
tadu 0.2.0
```

## Start a repository

`tadu init` adds the rule block (as `tadu sync` does), then creates `TODO.md` with the state legend and `TODO_LOG.md` with a log marker dated today. An existing `TODO.md` or `TODO_LOG.md` is left untouched, so it also completes a half-adopted repository; an existing rule block is updated as `sync` would. A directory or a dangling symlink in place of either file is refused before anything is written. Like `sync`, it prints what it would do and changes nothing until `--write`:

```bash
tadu init
tadu init --write
tadu doctor .
```

`init` writes no history index and claims no history coverage. To recover the open work buried in past agent conversations instead, use the `tadu-create` skill. `--file` selects the instruction file as it does for `sync`, and the exit status is `2` when the rule target or a backlog path is refused, in which case nothing is written.

With neither `AGENTS.md` nor `CLAUDE.md` present, `init` and `sync` create `AGENTS.md`. Claude Code reads `AGENTS.md` only when its AGENTS.md support is enabled, so in a repository worked with Claude Code add a `CLAUDE.md` containing the line `@AGENTS.md`. When both files exist, tadu uses the one that already holds the rule block, else `AGENTS.md`; so an `AGENTS.md` that a tool such as `next dev` creates later does not move the block.

## Check a repository

`tadu doctor` takes one or more repository roots and prints one line per finding, as `path:line: severity CODE message`. Line `0` means the finding is about the whole file.

```bash
tadu doctor .
```

```text
TODO_LOG.md:0: warning L004 no <!-- tadu:log v1 since YYYY-MM-DD --> marker; entries are checked as warnings
TODO_LOG.md:3: warning L002 entry has no Evidence: line
AGENTS.md:0: error R003 no TODO maintenance rule
```

Exit status: `0` when there are no errors (warnings alone still exit `0`), `1` when at least one error is reported. A clean repository prints nothing. Add `--json` for one JSON object per finding. A file that cannot be read as UTF-8 produces an `E001` finding and the other checks and roots still run.

doctor also finds what a tadu command stopped halfway (by Ctrl-C, a killed process or a crash) leaves behind. Each file is replaced by renaming a complete temporary copy over it, so no file is ever half written, but a command that writes two files can stop between them: a close in `TODO.md` and `TODO_LOG.md` (`T005`), a close of a task in `open/` and `closed/` (`J007`) a migration that left `TODO.md` or `TODO_LOG.md` beside `todo/` (`C004`), a `tadu migrate --recover` that did not finish (`C005`) and an `archive` that left tasks due to move (`C006`). Running the same command again finishes each of them (see the close, migrate and archive sections). A temporary `.<name>.<random>.tmp` copy, or the `.todo.migrating/` folder of a migration, is reported as `I001`; the next tadu write to the same folder removes temporary copies older than a minute, and `tadu migrate` starts over from a stale `.todo.migrating/`. Two log entries with the same `ID:` (`L007`, as an older tadu left when a stopped close was run again) are for you to merge by hand.

`tadu doctor --workspace DIR` checks the items of every repository registered in the workspace (paths are then optional; with only `--workspace`, the per-repository checks are not run). It reports unknown assignees of open items (`W001`), IDs shared between repositories (`W002`), repositories that could not be scanned (`W003`) and an invalid workspace (`W004`, an error). Giving neither paths nor `--workspace` exits `2`.

## List and show items

`tadu list` reads the open items of the repository roots given (default `.`) and prints one line per item as `repository:path:line [column] priority title`, with `-` for no priority and `due YYYY-MM-DD` after the priority when the item has a due date; an item with a `Kind:` shows it in the brackets, as `[backlog/decision]`, so a backlog without kinds prints exactly as before. The title is the item's first paragraph, so a hard-wrapped item shows whole; a title over 160 characters is cut to 157 plus `...` in this listing (`--json` and `show` stay full):

```bash
tadu list shop
```

```text
shop:TODO.md:10 [backlog] high **Checkout:** Reject duplicate webhook deliveries.
shop:TODO.md:14 [in_progress] - **Checkout:** Add the gift note field.
shop:TODO.md:16 [backlog/decision] high **Checkout:** Decide whether guest checkout keeps the phone field mandatory.
shop:TODO.md:26 [blocked] high **Shipping:** Switch to live carrier rates.
shop:TODO.md:34 [backlog/decision] - **Shipping:** Choose REST or SOAP for the carrier integration.
shop:TODO.md:38 [backlog/waiting] - **Shipping:** Carrier sends the production API key.
shop:TODO.md:48 [backlog/later] - **Billing:** Check whether retries dropped after the fix.
shop:TODO.md:54 [backlog/task] - **Billing:** Move invoices to the new VAT rate.
```

The kind tells the work you can do apart from the rest: `Kind: task` for work you can do, `Kind: decision` for a choice that must be made, `Kind: waiting` for something another person or organization owes, `Kind: later` for something not to do now. An item without `Kind:` is unclassified; tadu never guesses a kind from the text, and `--kind unclassified` lists what is left to sort. Three dates keep apart what used to share `Due:`: `Due:` is the deadline, `Check on:` the day to look at the item again (chase it, revisit it, verify it) and `Not before:` the day before which it cannot start. The kind never changes an item's state or column, and a blocked `[!]` item may be of any kind; the spec's Item kinds section says what to write in each. `--kind` and `--check-before` filter on them, and `next`, `inbox` and `urgent` (below) read them to say who has to act. A task backlog (format 2) has the same three as its `kind`, `check_on` and `defer_until` keys, so all of this works the same there.

`--json` prints one object per item; its keys are listed in the spec. The filters are `--project`, `--org`, `--role`, `--assignee`, `--column`, `--priority`, `--kind` (a kind or `unclassified`), `--label`, `--due-before`, `--check-before` and `--include-cancelled`, and, for an agent aiming at the right items without reading the files, `--category` and `--type` (comma-separated, any of), `--milestone`, `--text REGEX` (over title and text), `--due-within N` (overdue included), `--overdue`, `--min-priority`, `--open` (open items only: closed ones are not even read, so it is the fastest query for pending work) and `--history` (closed items of all time instead of `--done-days`). `--sort priority|due|closed` orders them. At most `--limit` items print (default 100, `0` for all), from `--offset`; when more match, a note on standard error says how many and how to get them, so a long answer is never cut short silently (a pipe such as `tadu list | grep` sees only that page: add `--limit 0`). A task of a task backlog prints as `repository:t-8c41d2e7 [column] priority title`, its shortest unique id prefix. `--workspace DIR` reads every repository of a workspace instead of paths; giving both exits `2`. A path is named by its directory, unless another path given has a directory of the same name: then both are named by their full path, so `~/acme/api` and `~/globex/api` never look alike. A directory given twice is read once. `--view NAME` applies a saved view of the workspace (see below); filter flags given beside it win, and it needs `--workspace`. Done and cancelled items come from `TODO_LOG.md` entries of the last `--done-days` days (default 14). Repositories that cannot be scanned are reported on standard error and do not change the exit status.

`tadu show KEY` prints the full text of one item, or with `--json` the same object as `list`, followed by the relations that point at it (what it blocks, its duplicates, what was discovered from it). A task id may be given as a unique prefix of at least 10 characters; an ambiguous prefix lists the candidates. An item without an `ID:` field has a derived key, which `list --json` shows. It exits `1` when no item has that key. Items may carry optional `ID:`, `Priority:`, `Assignees:`, `Due:`, `Check on:`, `Not before:`, `Labels:`, `Queue:`, `Kind:` and `Estimate:` fields, described in the spec; `doctor` warns about malformed ones (`F001`), repeated IDs (`F002`), field lines that are not read (`F003`) and fields that contradict each other or the item's state (`F004`), such as `Not before:` after `Due:` or `Kind: later` on an item in progress.

`tadu ready` prints the open items nothing holds back, most urgent first: pending and in-progress items with no open `blocked_by` task and no future `defer_until` (format 2). It takes the same paths or `--workspace`, `--json`, `--limit` and `--offset`.

`tadu similar "TEXT"` prints the open and closed items of all time most like the text, best first, each with the share of words they have in common (0 to 1). Run it before adding an item: deciding whether one of them is the same work is the agent's call. `--limit` (default 5) and `--open` narrow it.

`tadu feed` is the recently-done feed: the done and cancelled `TODO_LOG.md` entries of the last `--done-days` days (default 14), newest first by their closing date, one JSON object per line with the same keys as `list --json`. It takes the same repository paths or `--workspace DIR`; entries closed on the same day keep their repository and log order.

## Ask what to do next

Three commands answer what people ask of an agent. Each reads open items only, most pressing first (priority, then the earliest date, then started before ready before backlog), takes repository paths or `--workspace DIR` and `--json`, and prints items as `list` does. On standard error each says what else is open and which command lists it, so an agent that runs one finds the others.

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
shop:TODO.md:34 [backlog/decision] - **Shipping:** Choose REST or SOAP for the carrier integration.

Chase: waiting on others, follow-up due
shop:TODO.md:38 [backlog/waiting] - **Shipping:** Carrier sends the production API key.

Check: items whose check date has come
shop:TODO.md:48 [backlog/later] - **Billing:** Check whether retries dropped after the fix.

Blocked: tasks that cannot go on
shop:TODO.md:26 [blocked] high **Shipping:** Switch to live carrier rates.
```

The same backlog answers the three questions directly: what depends on me is `tadu inbox --person ana` (or the workspace's `me`), what waits on others is `tadu list --kind waiting`, and what to check is the inbox's Check section or `tadu list --check-before <day>`. `tadu next` leaves out the VAT task until its `Not before:` day.

`inbox` and `urgent` group items under headings that say who acts: Do, Decide, Chase, Check and Blocked; with `--json` each object adds a `section` key (`do`, `decide`, `chase`, `check` or `blocked`) to the `list` keys. `next` and `inbox` act for `--person ID`, else the workspace's `me`: an item assigned only to others is left out and an unassigned one is anyone's. Without a person every item counts, and the inbox has no blocked tasks, since nobody is named on them.

An agent working alone takes its work from `next`. When it meets a question only a person can answer, it records the question with `tadu add --kind decision` and the options as notes, blocks the task with `tadu mark --state blocked --note` naming the decision and goes on with the next task; `inbox` shows the decision when the person is back, and once it is closed `tadu mark --state open` reopens the task.

## Add an item

`tadu add` writes one new open item into `TODO.md`: last in its `## --category` section (created at the end of the file when missing, and the title gets the `**Category:**` prefix), else at the end. Like `close`, it prints the diff and changes nothing until `--write`, after which it runs `doctor`:

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

The item gets a new `ID:` unless `--no-id`, then the fields given (`--kind`, `--priority`, `--assignees`, `--due`, `--check-on`, `--not-before`, `--labels`, `--queue`, `--estimate`; without `--kind` the item is left unclassified), then one paragraph per `--note`. A value the fields table does not allow, a blank or multi-line argument, a category containing `*` and a note that would read as a field, a list item or a fence exit `2` before anything is written. A `TODO.md` with irregular line endings or an unclosed fence is refused, and so is a change that would give `doctor` an error; the write is atomic, under the same lock as `close`, and only when the file did not change since it was read. The options of a task backlog are written in their format 1 spelling: `--label` and `--assignee` join `Labels:` and `Assignees:`, `--defer-until` is `Not before:`, each `--done-when` a `Done when:` paragraph and `--blocked-by` (whole task ids) a `Depends on:` paragraph, as `tadu migrate` reads them back; `--type`, `--milestone`, `--parent`, `--discovered-from`, `--created-by`, `--related` and `--link` have no place in `TODO.md` and are refused, never dropped.

## Change an item's state or fields

`tadu mark` also sets or changes a field without editing `TODO.md`: `--kind`, `--priority`, `--assignees`, `--due`, `--check-on`, `--not-before`, `--labels`, `--queue` and `--estimate`, checked like `add`'s. An existing field line is replaced in place; a missing one is added as the item's last paragraph. `--state` is optional when a field is given; a field cannot be cleared this way.

```bash
tadu mark --match "Decide the limit" --kind decision --priority high --write
```

It sets the state of the one open item whose first line contains `--match`: `--state blocked` (`[!]`), `open` (`[ ]`) or `in_progress` (`[~]`). `--note` adds a paragraph at the end of the item, and blocking needs one, since a blocked item names its blocker. It prints the diff and writes only with `--write`, with the same checks, lock and refusals as `add`; no match or more than one exits `2` and lists the candidates.

```bash
tadu mark --match "over 10,000 EUR" --state blocked \
  --note 'Blocked on the decision "Raise the acquirer limit or split large charges".' --write
tadu mark --match "over 10,000 EUR" --state open --note "Decided: split charges above 10,000 EUR." --write
```

## Agent tools over MCP

`tadu mcp` is a [Model Context Protocol](https://modelcontextprotocol.io) server on standard input and output, built on no MCP library. An agent connected to it sees eight tools with their descriptions and a short usage note, so it needs no rule in `AGENTS.md` or `CLAUDE.md` to know when to use them:

| Tool | Does | Writes |
| ---- | ---- | ------ |
| `next`, `inbox`, `urgent` | what the commands of the same name print | no |
| `list`, `show` | the `list` filters (`kind`, `priority`, `column`, `assignee`, `label`, `due_before`, `check_before`, `open`) and one item by key | no |
| `add` | `tadu add --write` | `TODO.md` |
| `mark` | `tadu mark --write` | `TODO.md` |
| `close` | `tadu close --write` with `evidence` or `resolution` | `TODO.md` and `TODO_LOG.md` |

Each call runs the tadu command of that name, so a tool answers exactly as the command line does, checks included; a refused call comes back as a tool error with the command's message. The server reads the repository it starts in, the roots it is given, or `--workspace DIR`. `add`, `mark` and `close` write to exactly one repository: the only one the server reads, or the one named by `repository`, which is the name items show (the workspace key, the directory name, or the full path of directories that share a name) or an absolute path. A directory name two repositories share and a relative path never choose one; the call fails and lists the repositories by full path.

In Claude Code, for one project:

```bash
claude mcp add tadu -- tadu mcp
```

or in the project's `.mcp.json`, with `"args": ["mcp", "--workspace", "/path/to/workspace"]` to serve a workspace:

```json
{ "mcpServers": { "tadu": { "command": "tadu", "args": ["mcp"] } } }
```

In Codex, in `~/.codex/config.toml`:

```toml
[mcp_servers.tadu]
command = "tadu"
args = ["mcp"]
```

## Board

A workspace is a directory with a `tadu-workspace.toml` shared by the people who use it and an untracked `tadu-workspace.local.toml` that says where each repository is checked out on this machine. The smallest useful one:

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

[paths]
shop = "../shop"
```

Paths in `[paths]` are resolved: `~` expands and `..` is normalised. Projects, organizations with roles such as client and agency, remotes and an editor link template are optional; the spec has the full shape. A `[[view]]` table saves a named filter set (with the `list` filter names, `due_before` as a TOML date), such as `name = "my-urgent"`, `assignee = "ana"` and `priority = "urgent"`, for `tadu list --workspace . --view my-urgent`. Then:

```bash
tadu doctor --workspace .
tadu board --workspace .
```

`board` prints a URL such as `http://127.0.0.1:41873/?token=...`; open it. The files are rescanned on every request and on Reload. While it is visible, the page checks every 30 seconds that the board still answers to its token: when the board stops, it clears itself until the board is back, then reloads; after a restart, whose token is new, it clears itself and asks for the new URL. Options: `--host` (default `127.0.0.1`), `--port` and `--done-days` (default 14), each of which a [config file](#config-file) can also set. Without `--port` the board listens on a port derived from the workspace path (40000 to 49999), so the URL, and the saved views the browser keeps for it, stay the same across restarts; when that port is busy it takes any free port and says so on standard error. `--port 0` asks for any free port; port 80 also accepts the bare host, since browsers omit it.

The page has six views in its sidebar: My work (open items assigned to `me`), All work, Blocked (all, blocked for me, unassigned), Portfolio, Done (closed in the window, by day) and Board (a column per state, at most 30 cards each, with a link to the full list).

Every view, and every count on the page, shows one scope: a company, one of its projects and one of their repositories, chosen with the three pickers at the top, the Companies section of the sidebar or the Scope & filters popover. A project's company is the organization it lists under the role `company`; other roles, such as `client`, are relations: they show as badges ("Client: Automate Texas") and never as ownership. Projects that name no company sit under No company, and repositories in no project under No project. Picking a project sets its company, picking a repository its project, and clearing a level clears the levels below it. The scope stays as you switch views, is kept per workspace in the browser, and is part of the address (`#company=...&project=...&repository=...&view=...`), so a copied URL reopens the same view and scope. Star a scope to keep it in the sidebar; the last five scopes used are listed under Recent. A workspace without projects has only the repository picker.

Portfolio counts the scope as a tree, Company > Project > Repository, where each project appears once under the company that owns it and every row sums distinct repositories; Group: Client lists the projects under their client organizations instead. A row's name opens its items in its scope, its blocked count the Blocked view of them. Cards and rows name their company, project and repository; under 720 px the portfolio becomes one card per company.

A search box, a filters popover (assignee, priority, kind, label, state, due before, role, organization and the toggles, where Waiting on me shows what `tadu inbox` lists for `me`) with removable chips, grouping and sorting apply to every list; a decision, waiting or later item carries a badge saying so and a `Check on:` day shows beside the due date, and Group: Kind splits any list into tasks, decisions, waiting on others and later (grouped or filtered by kind, the headings or the chip name the kind and the badges are left out); lists draw only the rows on screen, so a workspace of thousands of items stays fast. Clicking an item opens its detail: full text, company, project, repository and relations, location, ID, fields, parse warnings and the links to the editor and the forge. Keys: `/` or Cmd/Ctrl-K search, G then S opens the scope switcher (type to find a company, project or repository, arrows and Enter to choose), J and K move, Enter opens the detail, E opens the editor, Esc closes. Saved views (with their scope), starred and recent scopes and the light or dark theme are kept in the browser's `localStorage`; under 720 px the page becomes a list with a bottom bar.

The board only reads. It writes no backlog, workspace or index file, and it cannot change a card: every request other than GET answers `405` with `Allow: GET`. With GitHub sign-in (see [below](#a-board-for-a-team-sign-in-with-github)), the board also writes `tadu-workspace.github-ids.json` and `tadu-workspace.sessions.json`, and a POST signs out. Edit the `TODO.md` files, or use `tadu close`.

Who may read it:

- The server checks the `Host` header against the address and port it is bound to (bound to `127.0.0.1`, it also accepts `localhost:<port>`) and answers `421` otherwise, which defeats DNS rebinding.
- The page and its scripts and stylesheet need only that; the server serves only files directly inside its own `board` directory. The card data at `/api/cards` also needs the per-run token, given as an `X-Tadu-Token` header or a `?token=` parameter; a missing or wrong token answers `403`. The page keeps the token in `sessionStorage` and removes it from the address bar.
- No response carries a CORS header, so another page cannot read the data. Responses send `Referrer-Policy: no-referrer`, `Cache-Control: no-store` and a Content-Security-Policy that allows only the page's own script and style.
- Item text is escaped, never rendered as HTML: only `**bold**` and `` `code` `` in titles are styled, built as elements holding plain text.
- `--host` other than `127.0.0.1` or `localhost` prints a warning: the server listens on that address, but it still serves only requests whose `Host` header is exactly `<host>:<port>`, so a browser that reaches it by any other name or address gets `421`. `::1` is not supported. An invalid workspace or a port that cannot be bound exits `2`.

### A board for a team: sign in with GitHub

With `--auth github`, the board serves a team: people sign in with their GitHub account, and each of them sees only the items of the workspace repositories they can read on GitHub. [docs/team-board.md](https://github.com/syntopica/tadu/blob/main/docs/team-board.md) is the full guide: registering the GitHub App, preparing the workspace, running behind https, the ids file, how much GitHub is asked, the security model, the limits and troubleshooting.

```bash
export TADU_GITHUB_CLIENT_ID=Iv23liAbCdEf0123
export TADU_GITHUB_CLIENT_SECRET=...   # never on the command line
tadu board --workspace . --auth github --port 8123 --public-url https://board.example.com
```

- Register a GitHub App whose callback URL is the public URL plus `/auth/callback` and which needs no permission beyond the default read-only Metadata, and install it on the organizations that own the repositories. An OAuth App works too, but must ask for the `repo` scope, which allows writing.
- Every workspace repository needs a `remote` on `github.com`; one without is shown to nobody, and `board` says so when it starts. Give each `[[person]]` their login (`github = "octocat"`) so that they are `me` when they sign in.
- Serve it behind a reverse proxy that terminates https, on a subdomain (`https://tadu.example.com`), a domain of its own, or a subfolder of another site (`https://example.com/tadu`, with the proxy keeping or taking away the `/tadu` prefix). `--public-url` is the address people open; it is only valid with `--auth github`. Prefer a subdomain or own domain: in a subfolder, the site's other pages share the board's origin. The guide has Caddy and nginx configurations for each.

What it guarantees:

- Access is checked with each person's own GitHub token, from their repository list with ETags, so a 100-repository workspace costs one or two requests per person every 5 minutes, nearly all of them free `304`s. Repositories they cannot read are not even scanned for them, and nothing about them reaches their browser: not items, keys, projects, organizations, saved views or scan problems.
- Each workspace repository is tied to its GitHub repository id, learned into `tadu-workspace.github-ids.json` beside the workspace file (or given as `github_id` on the `[[repository]]`), so a private repository renamed away and replaced by another under its old name is hidden from everyone, also after a restart.
- When in doubt it hides: a repository that cannot be checked (rate limit, GitHub down, SAML) or whose identity cannot be confirmed is hidden, with a notice that names nothing, and the operator gets the details on standard error.
- Starting and finishing a sign-in is rate limited per address: 10 a minute each by default, as GitLab limits its sign-in paths, with `429` and `Retry-After` beyond it; `--sign-in-limit` (such as `5/minute;50/hour`, or `off`) changes it, and `--proxy-hops 1` reads the client's address from a trusted reverse proxy.
- Sessions last while they are used: they end after 14 days of inactivity, or the `--idle-timeout` given, such as `8h`; clicking, typing or scrolling on an open page counts as activity, and the page warns 5 minutes before the end, GitHub tokens are renewed in the background, and sessions survive restarts: they are saved in `tadu-workspace.sessions.json` (keep it out of git), each sealed with `cryptography`'s Fernet under a key only the person's cookie gives, so the file signs nobody in and holds no usable token. Cookies are `HttpOnly`, `SameSite=Lax`, and `Secure` and `__Host-` prefixed behind https; signing out ends the session, and a token GitHub refuses ends it within 5 minutes.
- Signing in uses PKCE and GitHub's account picker (so a shared computer does not sign the next person in as the last), signing out has GitHub revoke the token, and only the board's own page may load its data, check the session or sign out: pages of other sites, and of other origins of the same site, are refused.

Its limits, in short: github.com only (no GitHub Enterprise Server), one process per workspace, access changes on GitHub take effect within 5 minutes, items are what the server's checkouts hold (pull them on a schedule), anyone with a GitHub account can sign in and sees the workspace's public repositories, and a board that first sees a repository after its name was taken over cannot tell unless `github_id` is set. The guide lists them all.

## Config file

Options you would give every time can live in a file instead; a flag on the command line always wins. The user's config file is `config.toml` in tadu's config directory (`~/.config/tadu/config.toml` on Linux, or under `$XDG_CONFIG_HOME`; `~/Library/Application Support/tadu/config.toml` on macOS; `%LOCALAPPDATA%\tadu\config.toml` on Windows), or the file `$TADU_CONFIG` or `--config FILE` names:

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

A workspace's `tadu-workspace.local.toml` takes the same tables, for the commands run on that workspace, and wins over the user's file. That is where a server keeps its board:

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

- **Order:** the command line, then the workspace's local file (`[command]`, then `[defaults]`), then the user's file (the same), then the built-in default. The workspace is `--workspace`, else the user's file's.
- **A repository keeps to itself.** A command that reads repositories (`list`, `show`, `next`, `inbox`, `urgent`, `ready`, `similar`, `feed`, `mcp`) ignores a workspace from a file when the command line names repository paths, or when it runs in a repository with a backlog (a `TODO.md` or `todo/tadu.json`), which is then its default path; a `view` from a file goes with it. So `tadu list .`, and an agent running `tadu next` in one repository, see that repository only, never the workspace's other items; `--workspace` still reaches the workspace from anywhere. `board` and `doctor`, which have no default path, use the configured workspace wherever they run.
- **Keys** are the long flags with `_` for `-` (`public_url` for `--public-url`), checked as the flag is: `port = 8123` or `"8123"`, `json = true`. `--no-json` turns off a `json = true`. A `workspace` in the user's file is relative to that file and may start with `~`; the local file cannot name one.
- **What a file can set:** where a command reads and how it prints or serves, never what one call acts on.

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

  Item selectors and contents (`--match`, `--id`, `--title`, `--evidence`, the `list` filters and the like) and `--write` stay on the command line, so a file can never make a command pick another item or write without being asked; a filter set you want by default is a saved `[[view]]`, named by `[list] view`. Who acts is not a setting either: `me` in the local file and `$TADU_ACTOR` say it. The GitHub client secret is read from the environment only.
- **The board's GitHub settings follow its `auth`.** `public_url`, `sign_in_limit`, `proxy_hops` and `idle_timeout` need `auth = "github"`; a file that sets them without it stops the board, naming the file. `--auth token` on the command line overrides a file's team board as a whole and drops the file's GitHub settings with it, so `tadu board --workspace /srv/team-workspace --auth token` is a private look at a server's workspace.
- **`--no-config`** (before or after the command) reads neither file's tables, for a script that must not depend on anyone's settings. MCP tool calls run that way, so a tool does what its description says.
- A file that cannot be used (unknown table or key, a value the flag would refuse, a missing file named by `--config` or `$TADU_CONFIG`) stops the command with exit `2`, naming the file, the table and the key. A value is checked when a command that uses it runs.

## Close an item

`tadu close` takes the one open item (`[ ]`, `[~]` or `[!]`, at the top level and outside fences) whose first line contains `--match`, removes it from `TODO.md` with its indented continuation lines, and writes it into `TODO_LOG.md` as a dated entry. `--evidence` logs it as `[x]`, `--resolution` as `[-]`; one of the two is required. Like `sync`, it prints the diff of both files and changes nothing until `--write`, after which it runs `doctor` on the repository and exits with its status:

```bash
tadu close --match "Fix the header" --evidence "tests/test_header.py passes" --result "The logo shows again" --write
```

```text
- [x] 2026-10-19 — **Frontend:** Fix the header
  - Result: The logo shows again
  - Evidence: tests/test_header.py passes
```

- The category is `--category`, else a `**Category:**` prefix the item already has, else the `##` section the item sits in, else `General`. `--title` replaces the item's text, and `--date YYYY-MM-DD` the date (default today). Continuation lines of the item are kept under the entry, before `Result:`.
- The entry goes under the `## YYYY` heading of its date, into the `### YYYY-MM` section, else a `###` section headed by that very day, else a new section; missing headings are created. Whether it goes at the top or the bottom of its section follows the order the log already keeps its dates in; with no clear order it is appended.
- No match, or more than one, exits `2` and lists the candidates with their line numbers. Blank or multi-line values exit `2`. Each file keeps its own line endings; a file mixing CRLF and LF, or holding a bare CR or a Unicode line separator, is refused, and so is an item whose indentation leaves a code fence open.
- A close whose result would give `doctor` an error the files did not already have is refused before anything is written. An item that was the last one leaves `TODO.md` with its legend.
- `TODO_LOG.md` is written first, then `TODO.md`, each atomically, under an exclusive lock on the repository directory (POSIX) and only when neither file changed since it was read. If the second write fails, the message names the line to delete by hand.
- A close stopped between the two writes (Ctrl-C, a killed process, a crash) leaves the item in both files, which `doctor` reports as `T005`. Run the same close again to finish it: the item is removed from `TODO.md` and nothing is logged twice. The entry already written is the record, so its date, title and category stay; evidence the new run gives that the entry lacks is added as another `Evidence:` line, and a `Result:` the entry has none of, or text the item gained since, goes in before its proof. Run on another day than the entry's, it adds that day as `Close run again: YYYY-MM-DD`, as the entry keeps its own. A close asking for another state, or another `Result:` or `Resolution:` than the entry has, is refused and names what is recorded, so nothing is replaced. Items without an `ID:` cannot be matched and are closed as usual.

## Task backlog (format 2)

A task backlog keeps each task in `todo/open/<id>.json` or `todo/closed/<id>.json`, with the settings in `todo/tadu.json`; the spec has every field. Start one, or convert a format 1 backlog (dry run first, as always):

```bash
tadu init --format 2 --write        # a new repository
tadu migrate                        # prints the plan
tadu migrate --write                # writes todo/, removes TODO.md and TODO_LOG.md (git keeps them)
```

A migration only ends once nothing of the Markdown files is missing from `todo/`, and then they are removed. Run on a task backlog with `TODO.md` or `TODO_LOG.md` still beside it (a migration that stopped, by this tadu or an older one; files edited or added since; a file written by hand next to `todo/`), `tadu migrate` completes it:

- each item becomes its task, or merges into the task already made of it: a task's own values are never replaced, and what the item holds that the task lacks (a line edited since, a value the task changed since) is added to its notes under a line saying where it came from;
- a `Kind:`, `Check on:` or `Not before:` line an older migrate left in the notes becomes its key, tasks take back the IDs an older migrate lost, and the headers are added to `tadu.json`;
- text of `TODO.md` outside its items is refused, as by a first migration, and a task file a newer tadu wrote is left as it is, keeping the Markdown files; a completion that stops is finished by running it again.

A backlog with an item a stopped close left both open and closed (`T005`) is refused by a first migration until that close is finished, or the task would be migrated twice.

An older tadu's migrate, whose files are gone, lost more: an `ID:` line with another line right below it (how `tadu close` writes a log entry), so the task got a new id, its `ID:` line stayed in its notes (`doctor` reports `J022`) and whatever named it points at nothing (`J012`); the `Kind:`, `Check on:` and `Not before:` fields, left as note lines; the words of a `Depends on:`, a value it could not parse, the first of a repeated field, the prose entries of the log and the headers. `tadu migrate --recover` brings them back from git. It reads `TODO.md` and `TODO_LOG.md` from the commit before the migration (the one that first added `todo/tadu.json`; failing that, the one before the latest commit that deleted them), or from `--from REV`, and completes the migration as above, but for what happened since: a task deleted since is not made again, and a value changed since stays without a note, as the change was yours. A task takes its real ID back in the folder it is in now (`open/`, `closed/` or `archive/`) and every relation naming the lost id follows; a real ID another task file has is refused and named, and so is an id doctor's `J005` or `J007` makes ambiguous. A recovery is done once per commit. Before it writes anything else, `todo/tadu.json` marks it pending (`x-format-1-recovering`), and `doctor` warns about it (`C005`) until a run of it finishes; a recovery that stops, at any point, or refuses something is therefore never silent, and running it again finishes it. A recovery from another commit waits until the pending one is finished. Once it finishes, the commit moves to `x-format-1-recovered`, and running it again from that commit (by any name) changes nothing, so a task, a note or a header it brought and you removed since stays removed; to redo a finished one, drop its commit from that list. Like every command it is a dry run until `--write`:

```bash
tadu migrate --recover          # lists each change
tadu migrate --recover --write
```

Legacy items convert to valid tasks: a title over 200 characters, or written as a bold lead sentence, keeps its first sentence and moves the rest into the notes; a done or cancelled item with no day, result, evidence or resolution gets the migration day and a "legacy item migrated without a recorded ..." line; a dated open item keeps its day as `created`. The plan lists any task that still fails the checks, so nothing is lost silently.

Fields are read as `doctor` reads them: a field line starts a paragraph, and only the first line of a name counts. Each one lands in the task key that holds it: `Kind:` is `kind`, `Check on:` is `check_on` and `Not before:` is `defer_until`. What no key can hold stays in the task's notes as its own line: a value that does not parse, a repeated field and `Queue: ready` on an item that is not pending. A migration never drops text:

- A line of `TODO.md` outside every item (a line after an item, a `###` subsection, a section without items) belongs to a task only a person can name, so the migration refuses, dry run included, and lists each such line with its file and line number; move it into an item, then run again.
- In `TODO_LOG.md`, each block written outside the dated entries, such as a prose entry of an old log, becomes a closed task holding the block whole in its notes. Only what is sure becomes a key: the title is its heading (or first line), and `closed` the day its heading gives; a month or a year gives its first day and the note says so, as it does that the log recorded no state or evidence. The plan lists these blocks.
- A `Depends on:` that says more than its task ids stays in the notes whole, besides giving `blocked_by`, and an entry without a closing day says in its notes that it is closed on the migration day.
- The header of each file (its title, the quoted summary such as a history coverage note, the log marker) is kept verbatim in `todo/tadu.json` as `x-format-1-header`.

Then work through the commands, never by editing the JSON by hand:

```bash
tadu add --title "Reject duplicate webhook deliveries" --category billing --type bug --priority high --write
tadu set t-8c41d2e7 due=2026-11-20 "labels+=webhooks" --write
tadu claim t-8c41d2e7 --as agent:claude --write
tadu close --id t-8c41d2e7 --evidence "pnpm test -- webhook-idempotency passes" --write
```

- `add` shows similar open and closed tasks before writing, and records `created` and `created_by` (`--created-by`, or `$TADU_ACTOR`). Repeatable options (`--label`, `--note`, `--done-when`, `--link`, `--blocked-by`, `--related`, `--assignee`) take one value each time; ids may be unique prefixes. `--kind` and `--check-on` are stored as `kind` and `check_on`; the format 1 spellings work too: `--not-before` is `defer_until`, and the comma lists of `--labels` and `--assignees` join the repeated ones. An option the task cannot hold is refused (`--no-id`, or `--not-before` and `--defer-until` on different days), never dropped.
- `set ID key=value ...` changes fields (`key+=v` and `key-=v` for lists, `key=` to remove); it never changes `id`, `started` or `closed`, and does not close a task.
- `claim` sets the assignee, `in_progress` and `started` at once; it refuses a blocked, deferred or closed task, and one someone else has in progress unless `--force`.
- `close` appends `closed`, `result` (default: the title) and `evidence` and moves the file to `closed/`, or cancels with `--resolution` or `--duplicate-of ID`. It reports each task that waited on the closed one and changes none of them; decide whether each moves to pending. `--match TEXT` picks the one open task whose title contains it. The closed file is written before the open one is deleted; a close stopped in between leaves both, which `doctor` reports as `J007`, and other commands on that task say so. Run the same close again (by `--id` or `--match`) to finish it, on the same terms as a format 1 close: the closed file's `closed` date, `result` and `resolution` stay, new evidence is appended, a result that was only the default (the title) takes the one given, and another state, result, resolution or duplicate is refused. An open copy edited since is refused too, with the keys that differ.
- `archive` moves old closed tasks to `todo/archive/YYYY/` (or `YYYY/MM/` for a busy year) as the archive policy in `tadu.json` says; without a policy nothing moves. `fmt` rewrites files that are not in canonical form.

Every command is a dry run until `--write`, exits `2` when it refuses, and validates before writing, so none can produce a file `doctor` would reject. Like the commands of a `TODO.md` backlog, they hold an exclusive lock on the repository directory (POSIX) while they read and write, so two of them never interleave. `doctor` checks a task backlog with the `C` and `J` codes below.

Reading a task backlog is fast for open work at any size (`list --open`, `ready`: about 0.4 s with 2,500 open tasks). Commands that go through all of history (`list --history`, the default `list` window, `similar`, `add`, `show` and `doctor`) read every task file once, then keep what they built in an item cache outside the repository: `$TADU_CACHE_DIR`, else the system's cache directory for tadu (`$XDG_CACHE_HOME/tadu` or `~/.cache/tadu` on Linux, `~/Library/Caches/tadu` on macOS, `%LOCALAPPDATA%\tadu\Cache` on Windows). Each run still checks every file's size, inode and timestamps and rebuilds only what changed, so an edit, a `git checkout` or a pull is always seen; files changed in the last two seconds are re-read until they are older. The cache holds plain JSON, never code, and nothing in the repository; delete it at any time, or set `TADU_NO_CACHE=1` to turn it off.

## Write the rule block

`tadu sync` puts the maintenance rule into the repository's instruction file between `<!-- tadu:rule v5 -->` and `<!-- /tadu:rule -->` marker lines. It edits `AGENTS.md`, or `CLAUDE.md` when there is no `AGENTS.md`. Run it without flags first: that prints a diff and changes nothing.

```bash
tadu sync .
```

```text
--- AGENTS.md
+++ AGENTS.md
@@ -1 +1,59 @@
 # Demo
+
+<!-- tadu:rule v5 -->
+
+## Continuous TODO, Work Log, and History Coverage
...
+<!-- /tadu:rule -->
```

Apply it with `--write`:

```bash
tadu sync . --write
tadu sync .
```

```text
AGENTS.md: up to date
```

- The write goes to a temporary file in the same directory that then replaces the target, so a failure never leaves a half-written file, and only when the file still holds what `sync` read: an edit made meanwhile is kept and `sync` exits `2` (a file that did not exist is created only if it still does not). Line endings (LF or CRLF) and file mode are kept, and only the text between the markers changes. A block that differs from the current one only in blank lines or soft line wrapping, as a Markdown formatter such as Prettier with `proseWrap` leaves it, counts as up to date; a changed word, list item, heading, hard line break or fenced line is still drift.
- Markers count only when they are a whole line outside a fenced code block, so quoting them in prose or in an example is safe.
- `--file docs/rules.md` selects another instruction file, given relative to the repository root. `sync` refuses a root that is not a directory and a file that resolves outside the root, and exits `2`; it also exits `2` for unbalanced markers and for a file that is not valid UTF-8.
- `--adopt-legacy` replaces an older, unmarked section headed "Continuous TODO" instead of appending a second rule. The section ends at the next Markdown heading of any level, at the next line starting with `<!--`, or at the end of the file. Use it only when that section holds nothing but the standard rule. When it holds repository-specific lines, run plain `tadu sync . --write` and keep those lines by hand under a "TODO conventions specific to this repository" heading after the block.

A repository synced before the current block version gets an `R004` warning; run `tadu sync . --write` to update it. Version 2 added the closed-entry template and names the `Evidence:` and `Resolution:` lines the log check requires; version 3 adds `tadu close`, tells agents to run `tadu doctor .` before committing, and says how to install tadu; version 4 adds item kinds and `next`, `inbox`, `urgent`, `add` and `mark`, so an agent working alone records a decision for a person instead of waiting for one, tells agents to query the backlog instead of reading it whole, to run `tadu similar` before adding an item, and how to work a task backlog (format 2) through its commands.

## Adopt the log check

Closed entries in `TODO_LOG.md` need an `Evidence:` (for `[x]`) or `Resolution:` (for `[-]`) line with content. Without a marker the check is only a warning, so that old history does not fail. A repository adopting the format inserts this line once, after the log header, with the adoption date:

```text
<!-- tadu:log v1 since 2026-10-12 -->
```

Entries dated on or after that day then need proof and a missing line is an error; older entries are legacy and are not checked.

## Enforce it

Run `doctor` on every commit with [pre-commit](https://pre-commit.com/). Pin `rev` to a tag or commit of this repository:

```yaml
repos:
  - repo: https://github.com/syntopica/tadu
    rev: <tag or commit>
    hooks:
      - id: tadu-doctor
```

Or as a CI step, pinned to a released version, with either runner:

```bash
uvx tadu@<version> doctor .
pipx run --spec tadu==<version> tadu doctor .
```

### After every agent edit, in Claude Code

`tadu hook claude` reads a Claude Code `PostToolUse` event on standard input. When the tool call changed a backlog file (an `Edit` or `Write` of `TODO.md`, `TODO_LOG.md`, `TODO_HISTORY_INDEX.jsonl` or a task file under `todo/`, a shell command that writes one, or a `tadu close`, `add`, `set`, `claim`, `archive`, `fmt` or `migrate` run with `--write`), it runs the doctor checks on that repository and hands any errors back to the agent as context. It prints nothing otherwise, never blocks the tool call and always exits `0`. Shell commands are matched as text and never run.

The plugin below installs it. Without the plugin, add it to `.claude/settings.json` or `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|Bash",
        "hooks": [{ "type": "command", "command": "tadu hook claude", "timeout": 20 }]
      }
    ]
  }
}
```

Both fail only on errors. Warnings, including an outdated rule block, do not block a commit.

Branches that close work in the same month both append to the same section of `TODO_LOG.md` and conflict when merged. Resolve the conflict by keeping both entries whole, then run `tadu doctor .`. Do not set `merge=union` for these files: it can interleave the lines of two entries and attach one entry's `Evidence:` to the other.

## Finding codes

| Code | Severity | Meaning |
| ---- | -------- | ------- |
| T001 | error | `TODO.md` is missing |
| T002 | warning | `TODO.md` does not quote the five state markers |
| T003 | error | a closed top-level item (`[x]` or `[-]`) is still in `TODO.md` |
| T004 | error | `TODO.md` is empty |
| T005 | error | an open item's `ID:` is on a closed `TODO_LOG.md` entry: a close stopped halfway; run it again |
| L001 | warning | `TODO_LOG.md` is missing |
| L002 | error (warning without the log marker) | a closed `[x]` entry has no `Evidence:` content |
| L003 | error (warning without the log marker) | an obsolete `[-]` entry has no `Resolution:` content |
| L004 | warning | the `tadu:log` marker is missing |
| L005 | error | the `tadu:log` marker date does not parse |
| L006 | warning | `TODO_LOG.md` is empty |
| L007 | warning | two `TODO_LOG.md` entries have the same `ID:`, as an older tadu left when a stopped close was run again |
| H001 | error | an index line is not a JSON object |
| H002 | error | an index record lacks a required key |
| H003 | error | `review_status` is not one of the known statuses |
| H004 | error | two index records share a `source` and `conversation_id` |
| H005 | warning | index records are not sorted by `source`, then `conversation_id` |
| H006 | error | an index field has the wrong type or an empty value |
| R001 | warning | there is no `AGENTS.md` or `CLAUDE.md` |
| R002 | warning | an unmarked legacy rule section exists |
| R003 | error | the instruction file has no TODO maintenance rule |
| R004 | warning | the marked rule block is older than the current version |
| R005 | error | the rule markers are not exactly one open followed by one close |
| F001 | warning | an item field is malformed |
| F002 | warning | an `ID:` is used by more than one open item |
| F003 | warning | a field line of an open item is not read: no blank line before it, or no value |
| F004 | warning | fields of an open item contradict each other or its state, such as `Not before:` after `Due:` |
| W001 | warning | an open item is assigned to someone who is not a person in the workspace |
| W002 | warning | an `ID:` is used in more than one repository of the workspace |
| W003 | warning | a workspace repository could not be scanned |
| W004 | error | the workspace file or local configuration is invalid |
| E001 | error | a file could not be read (not valid UTF-8, or an I/O error) |
| I001 | warning | a temporary file, or the `.todo.migrating/` folder, of a tadu write that stopped halfway |
| C001 | error | `todo/tadu.json` is missing |
| C002 | error | `todo/tadu.json` is not valid |
| C003 | warning | `todo/archive/` holds tasks but `tadu.json` has no archive policy |
| C004 | warning | a `TODO.md` or `TODO_LOG.md` next to a task backlog is ignored; `tadu migrate --write` brings what it holds into `todo/` and removes it |
| C005 | warning | a `tadu migrate --recover` started and did not finish (it stopped, or refused something); run it again |
| C006 | warning | closed tasks are due to move under the archive policy; `tadu archive --write` moves them |
| J001 | error | a task file is not JSON, not an object, or has no usable `tadu` version |
| J002 | warning | a task file from a newer format version: read, never rewritten |
| J003 | error | a task is invalid (missing key, bad value, or a rule of its state) |
| J004 | warning | a task file is not in canonical form; `tadu fmt` rewrites it |
| J005 | error | a task file's name differs from its id |
| J006 | error | a task is in the wrong folder for its state, or its archive year or month is wrong |
| J007 | error | two task files have the same id; in `open/` and `closed/`, a close stopped halfway: run it again |
| J008 | warning | a category is not declared in `tadu.json` |
| J009 | warning | a type is not declared in `tadu.json` |
| J010 | warning | an open task needs triage: priority `untriaged`, category `general` or type `untriaged` |
| J011 | warning | a task has an unknown key (kept; probably a typo) |
| J012 | error | a relation points to a task that does not exist |
| J013 | error | `blocked_by` relations form a cycle |
| J014 | warning | a blocked task's `blocked_by` tasks are all closed and it has no `blocker` |
| J015 | warning | a pending or in-progress task waits on an open `blocked_by` task |
| J016 | warning | a `blocked_by` task was cancelled |
| J017 | warning | a line of a task file looks like a secret (a private key; an AWS, Google, Azure, OpenAI or Anthropic key; a GitHub, GitLab, Slack, npm, PyPI, Stripe, SendGrid, Shopify, Square, Twilio or Mailchimp token; a password in a URL; a credential assignment); the value is never printed |
| J018 | warning | a task has been in progress longer than `stale_after_days` |
| J019 | warning | a milestone is not declared in `tadu.json` |
| J020 | error | a relation points to the task itself |
| J021 | warning | `duplicate_of` points to a task that is itself a duplicate |
| J022 | warning | the notes hold an `ID:` line of another id: the task's ID, which an older tadu's migrate lost; `tadu migrate --recover` gives it back |
| J023 | warning | keys of an open task contradict each other or its state: `defer_until` or `check_on` after `due`, in progress while `defer_until` is ahead or `kind` is later, `queue` ready on a waiting or later task (format 1's `F004`) |

## Skills

Two agent skills ship with the format, and the Claude Code plugin also installs the hook above (it stays silent when `tadu` is not installed):

- `tadu-create` builds `TODO.md`, `TODO_LOG.md` and the history index from the project's agent conversation history.
- `tadu-work` executes an existing backlog under an approved plan and run caps.

In Claude Code:

```text
/plugin marketplace add syntopica/tadu
/plugin install tadu@tadu
```

For other agents, copy `skills/<name>/` into the agent's skills directory.

## License

MIT

## Working on tadu

`uv run pytest` runs the test suite, in parallel (pytest-xdist, one worker per core; add `-n 0` for one process, as a debugger needs); with `--cov=tadu` it must keep 100% coverage. It leaves out the crash tests, which take a few minutes on one core and under a minute on four: `uv run pytest -m crash` stops every command that writes (each format's `init`, `add`, `mark`, `set`, `claim`, `close`, `fmt`, `archive`, `migrate`, its completion and `--recover`) right before each filesystem change it makes, with SIGKILL (no cleanup runs) and with Ctrl-C, in a real process. After each stop, `doctor` must tell every half-done state from a finished one (there is no exception), and the same command run again must end exactly as it does when nothing stops it; the commands that only read must write nothing. Run them before changing how a command writes. `tests/fixtures/old_migration` is what an older tadu's migrate wrote of a backlog, kept to test `--recover` and the completion of an older migration.
