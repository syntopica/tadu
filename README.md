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
- `tadu board` serves a read-only kanban page for a workspace.
- `tadu hook claude` is a Claude Code hook that runs `doctor` after an agent changes the backlog.
- `tadu mcp` serves `next`, `inbox`, `urgent`, `list`, `show`, `add`, `mark` and `close` as tools an agent sees without any instruction file.

Contributors need none of it: the rule block that `sync` writes into `AGENTS.md` or `CLAUDE.md` tells any agent, or any person, how to add an item and how to log closed work in a shape `doctor` accepts.

## Requirements

Python 3.12 or newer. tadu has no runtime dependencies; [uv](https://docs.astral.sh/uv/) is only needed to work on tadu itself.

## Install

tadu needs Python 3.12 or newer and nothing else. Install it as a command with any Python installer:

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

The kind tells the work you can do apart from the rest: `Kind: task` for work you can do, `Kind: decision` for a choice that must be made, `Kind: waiting` for something another person or organization owes, `Kind: later` for something not to do now. An item without `Kind:` is unclassified; tadu never guesses a kind from the text, and `--kind unclassified` lists what is left to sort. Three dates keep apart what used to share `Due:`: `Due:` is the deadline, `Check on:` the day to look at the item again (chase it, revisit it, verify it) and `Not before:` the day before which it cannot start. The kind never changes an item's state or column, and a blocked `[!]` item may be of any kind; the spec's Item kinds section says what to write in each. `--kind` and `--check-before` filter on them, and `next`, `inbox` and `urgent` (below) read them to say who has to act.

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

The item gets a new `ID:` unless `--no-id`, then the fields given (`--kind`, `--priority`, `--assignees`, `--due`, `--check-on`, `--not-before`, `--labels`, `--queue`, `--estimate`; without `--kind` the item is left unclassified), then one paragraph per `--note`. A value the fields table does not allow, a blank or multi-line argument, a category containing `*` and a note that would read as a field, a list item or a fence exit `2` before anything is written. A `TODO.md` with irregular line endings or an unclosed fence is refused, and so is a change that would give `doctor` an error; the write is atomic, under the same lock as `close`, and only when the file did not change since it was read.

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

`tadu mcp` is a [Model Context Protocol](https://modelcontextprotocol.io) server on standard input and output, with no dependencies. An agent connected to it sees eight tools with their descriptions and a short usage note, so it needs no rule in `AGENTS.md` or `CLAUDE.md` to know when to use them:

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

`board` prints a URL such as `http://127.0.0.1:41873/?token=...`; open it. The files are rescanned on every request and on Reload. Options: `--host` (default `127.0.0.1`), `--port` and `--done-days` (default 14). Without `--port` the board listens on a port derived from the workspace path (40000 to 49999), so the URL, and the saved views the browser keeps for it, stay the same across restarts; when that port is busy it takes any free port and says so on standard error. `--port 0` asks for any free port; port 80 also accepts the bare host, since browsers omit it.

The page has six views in its sidebar: My work (open items assigned to `me`), All work, Blocked (all, blocked for me, unassigned), Portfolio, Done (closed in the window, by day) and Board (a column per state, at most 30 cards each, with a link to the full list).

Every view, and every count on the page, shows one scope: a company, one of its projects and one of their repositories, chosen with the three pickers at the top, the Companies section of the sidebar or the Scope & filters popover. A project's company is the organization it lists under the role `company`; other roles, such as `client`, are relations: they show as badges ("Client: Automate Texas") and never as ownership. Projects that name no company sit under No company, and repositories in no project under No project. Picking a project sets its company, picking a repository its project, and clearing a level clears the levels below it. The scope stays as you switch views, is kept per workspace in the browser, and is part of the address (`#company=...&project=...&repository=...&view=...`), so a copied URL reopens the same view and scope. Star a scope to keep it in the sidebar; the last five scopes used are listed under Recent. A workspace without projects has only the repository picker.

Portfolio counts the scope as a tree, Company > Project > Repository, where each project appears once under the company that owns it and every row sums distinct repositories; Group: Client lists the projects under their client organizations instead. A row's name opens its items in its scope, its blocked count the Blocked view of them. Cards and rows name their company, project and repository; under 720 px the portfolio becomes one card per company.

A search box, a filters popover (assignee, priority, kind, label, state, due before, role, organization and the toggles, where Waiting on me shows what `tadu inbox` lists for `me`) with removable chips, grouping and sorting apply to every list; a decision, waiting or later item carries a badge saying so and a `Check on:` day shows beside the due date, and Group: Kind splits any list into tasks, decisions, waiting on others and later (grouped or filtered by kind, the headings or the chip name the kind and the badges are left out); lists draw only the rows on screen, so a workspace of thousands of items stays fast. Clicking an item opens its detail: full text, company, project, repository and relations, location, ID, fields, parse warnings and the links to the editor and the forge. Keys: `/` or Cmd/Ctrl-K search, G then S opens the scope switcher (type to find a company, project or repository, arrows and Enter to choose), J and K move, Enter opens the detail, E opens the editor, Esc closes. Saved views (with their scope), starred and recent scopes and the light or dark theme are kept in the browser's `localStorage`; under 720 px the page becomes a list with a bottom bar.

The board only reads. It writes no backlog, workspace or index file, and it cannot change a card: every request other than GET answers `405` with `Allow: GET`. Edit the `TODO.md` files, or use `tadu close`.

Who may read it:

- The server checks the `Host` header against the address and port it is bound to (bound to `127.0.0.1`, it also accepts `localhost:<port>`) and answers `421` otherwise, which defeats DNS rebinding.
- The page and its scripts and stylesheet need only that; the server serves only files directly inside its own `board` directory. The card data at `/api/cards` also needs the per-run token, given as an `X-Tadu-Token` header or a `?token=` parameter; a missing or wrong token answers `403`. The page keeps the token in `sessionStorage` and removes it from the address bar.
- No response carries a CORS header, so another page cannot read the data. Responses send `Referrer-Policy: no-referrer`, `Cache-Control: no-store` and a Content-Security-Policy that allows only the page's own script and style.
- Item text is escaped, never rendered as HTML: only `**bold**` and `` `code` `` in titles are styled, built as elements holding plain text.
- `--host` other than `127.0.0.1` or `localhost` prints a warning: the server listens on that address, but it still serves only requests whose `Host` header is exactly `<host>:<port>`, so a browser that reaches it by any other name or address gets `421`. `::1` is not supported. An invalid workspace or a port that cannot be bound exits `2`.

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

## Task backlog (format 2)

A task backlog keeps each task in `todo/open/<id>.json` or `todo/closed/<id>.json`, with the settings in `todo/tadu.json`; the spec has every field. Start one, or convert a format 1 backlog (dry run first, as always):

```bash
tadu init --format 2 --write        # a new repository
tadu migrate                        # prints the plan
tadu migrate --write                # writes todo/, removes TODO.md and TODO_LOG.md (git keeps them)
```

Legacy items convert to valid tasks: a title over 200 characters, or written as a bold lead sentence, keeps its first sentence and moves the rest into the notes; a done or cancelled item with no day, result, evidence or resolution gets the migration day and a "legacy item migrated without a recorded ..." line; a dated open item keeps its day as `created`. The plan lists any task that still fails the checks, so nothing is lost silently.

Then work through the commands, never by editing the JSON by hand:

```bash
tadu add --title "Reject duplicate webhook deliveries" --category billing --type bug --priority high --write
tadu set t-8c41d2e7 due=2026-11-20 "labels+=webhooks" --write
tadu claim t-8c41d2e7 --as agent:claude --write
tadu close --id t-8c41d2e7 --evidence "pnpm test -- webhook-idempotency passes" --write
```

- `add` shows similar open and closed tasks before writing, and records `created` and `created_by` (`--created-by`, or `$TADU_ACTOR`). Repeatable options (`--label`, `--note`, `--done-when`, `--link`, `--blocked-by`, `--related`, `--assignee`) take one value each time; ids may be unique prefixes.
- `set ID key=value ...` changes fields (`key+=v` and `key-=v` for lists, `key=` to remove); it never changes `id`, `started` or `closed`, and does not close a task.
- `claim` sets the assignee, `in_progress` and `started` at once; it refuses a blocked, deferred or closed task, and one someone else has in progress unless `--force`.
- `close` appends `closed`, `result` (default: the title) and `evidence` and moves the file to `closed/`, or cancels with `--resolution` or `--duplicate-of ID`. It reports each task that waited on the closed one and changes none of them; decide whether each moves to pending. `--match TEXT` picks the one open task whose title contains it.
- `archive` moves old closed tasks to `todo/archive/YYYY/` (or `YYYY/MM/` for a busy year) as the archive policy in `tadu.json` says; without a policy nothing moves. `fmt` rewrites files that are not in canonical form.

Every command is a dry run until `--write`, exits `2` when it refuses, and validates before writing, so none can produce a file `doctor` would reject. `doctor` checks a task backlog with the `C` and `J` codes below.

Reading a task backlog is fast for open work at any size (`list --open`, `ready`: about 0.4 s with 2,500 open tasks). Commands that go through all of history (`list --history`, the default `list` window, `similar`, `add`, `show` and `doctor`) read every task file once, then keep what they built in an item cache outside the repository: `$TADU_CACHE_DIR`, else `$XDG_CACHE_HOME/tadu`, else `~/.cache/tadu`. Each run still checks every file's size, inode and timestamps and rebuilds only what changed, so an edit, a `git checkout` or a pull is always seen; files changed in the last two seconds are re-read until they are older. The cache holds plain JSON, never code, and nothing in the repository; delete it at any time, or set `TADU_NO_CACHE=1` to turn it off.

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
| L001 | warning | `TODO_LOG.md` is missing |
| L002 | error (warning without the log marker) | a closed `[x]` entry has no `Evidence:` content |
| L003 | error (warning without the log marker) | an obsolete `[-]` entry has no `Resolution:` content |
| L004 | warning | the `tadu:log` marker is missing |
| L005 | error | the `tadu:log` marker date does not parse |
| L006 | warning | `TODO_LOG.md` is empty |
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
| C001 | error | `todo/tadu.json` is missing |
| C002 | error | `todo/tadu.json` is not valid |
| C003 | warning | `todo/archive/` holds tasks but `tadu.json` has no archive policy |
| C004 | warning | a `TODO.md` next to a task backlog is ignored |
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
