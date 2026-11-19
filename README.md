# tadu

**A backlog that lives in your repository, kept honest for coding agents.**

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

tadu keeps a repository's open work and its closed work in plain files next to the code, and
gives agents and people the commands to read and change them without breaking the format. Work
is closed with proof (the test, command or PR that shows it is done), a checker guards every
commit, and git keeps every change, which `tadu show --history` reads back.

```console
$ tadu add --title "Reject duplicate webhook deliveries" --category Checkout --kind task --priority high --write
...
TODO.md:10: added t-006963ad-a372-4ff8-9f5e-60eb23230b7f
$ git commit -qam "Add the webhook task"

$ tadu next
shop:TODO.md:10 [backlog/task] high **Checkout:** Reject duplicate webhook deliveries

$ tadu close --match "duplicate webhook" --evidence "pytest tests/test_webhooks.py passes" --write
...
$ git commit -qam "Fix duplicate webhook deliveries"

$ tadu show t-006963ad --history
- [x] 2026-11-18 — **Checkout:** Reject duplicate webhook deliveries
  ...
  - Evidence: pytest tests/test_webhooks.py passes

2026-11-18 05:24  4dfc27ef4e  Ana  Fix duplicate webhook deliveries
  file: TODO.md → TODO_LOG.md
  state: pending → done
  day: none → 2026-11-18
  + - Evidence: pytest tests/test_webhooks.py passes

2026-11-18 05:24  10027e6b67  Ana  Add the webhook task
  created in TODO.md
  ...
```

**Contents:** [Why tadu](#why-tadu) · [Install](#install) · [Quick start](#quick-start) ·
[How it works](#how-it-works) · [Commands](#commands) · [Guides](#guides) ·
[Documentation](#documentation) · [Development](#development) · [License](#license)

## Why tadu

- **Plain text in git.** `TODO.md` and `TODO_LOG.md`, or one JSON file per task. Nothing to host,
  reviewed in pull requests like code.
- **Made for agents.** Agents query the backlog instead of reading it whole (`list`, `next`,
  `inbox`, `urgent`), get it as [MCP](https://github.com/syntopica/tadu/blob/main/docs/agents.md#mcp-server) tools, and follow a rule block
  that `tadu sync` writes into `AGENTS.md` or `CLAUDE.md`.
- **Closed means proven.** Closing records a result and its evidence, and `tadu doctor` fails the
  commit when proof is missing or the format is broken.
- **History for free.** `tadu show --history` shows every change to an item from git, through
  closing, archiving and migration between formats, and `tadu changes` what changed across the
  backlog in a sprint: what was closed and by whom, what got reopened.
- **Scales to parallel work.** The task-file format merges cleanly when several agents work on
  branches, and stays fast with tens of thousands of tasks.
- **Many repositories, one view.** A workspace reads them together, and `tadu board` serves a
  kanban page: read-only by default, or where cards are dragged and changed with `--allow write`.
- **One set of commands.** The command line, the MCP tools and the board are the same
  operations, declared once, with the same arguments and checks, and permissions per server and
  per repository.
- **Safe by default.** Every command that writes is a dry run until `--write`, and refuses any
  change that `doctor` would reject. No runtime dependencies.

## Install

tadu needs Python 3.12 or newer and nothing else. Install it as a command:

```bash
uv tool install tadu          # or: pipx install tadu, or: python3 -m pip install tadu
tadu --version
```

The development version installs from git the same way:
`uv tool install git+https://github.com/syntopica/tadu`.

## Quick start

In a git repository:

```bash
tadu init --write          # TODO.md, TODO_LOG.md and the agent rule block in AGENTS.md
tadu add --title "Reject duplicate webhook deliveries" --category Checkout --kind task --write
tadu list                  # what is open
tadu next                  # what an agent can do now, alone
tadu close --match "duplicate webhook" --evidence "pytest tests/test_webhooks.py passes" --write
tadu doctor .              # check the backlog; run it on every commit
```

Then let agents in: they read the rule block `init` wrote, or connect over MCP with
`claude mcp add tadu -- tadu mcp --allow write` (without `--allow write` they only read). To check every commit, add the
[pre-commit hook](https://github.com/syntopica/tadu/blob/main/docs/doctor.md#enforce-it).

## How it works

### The files

A repository keeps its backlog in one of two formats:

| | Format 1: Markdown | Format 2: task files |
| - | - | - |
| Open work | `TODO.md` | `todo/open/<id>.json` |
| Closed work | `TODO_LOG.md`, old years in `docs/todo-log/YYYY.md` | `todo/closed/`, old tasks in `todo/archive/` |
| Settings | — | `todo/tadu.json`: categories, types, milestones, policies |
| Best for | a small backlog people also read and edit | large backlogs, many agents on parallel branches |
| Spec | [todo-format-v1.md](https://github.com/syntopica/tadu/blob/main/spec/todo-format-v1.md) | [todo-format-v2.md](https://github.com/syntopica/tadu/blob/main/spec/todo-format-v2.md) |

The reading commands, `doctor`, `add` and `close` work with both; `tadu migrate` converts format 1
to format 2. An optional
`TODO_HISTORY_INDEX.jsonl` records which past agent conversations were already reviewed.

In format 1, an item is a Markdown checklist entry with optional fields, and a closed item moves
to the log with its proof:

```markdown
- [ ] **Shipping:** Choose REST or SOAP for the carrier API

  ID: t-a8ca470d-03c2-4bfb-a9d0-c855e8cf5911

  Kind: decision

  REST is newer; SOAP has the rate endpoint.
```

```markdown
- [x] 2026-11-18 — **Checkout:** Reject duplicate webhook deliveries
  - Result: A replayed delivery returns 200 without a second row
  - Evidence: pytest tests/test_webhooks.py passes
```

### States, kinds and fields

| State | Format 1 | Format 2 | Column |
| ----- | -------- | -------- | ------ |
| pending | `[ ]` | `pending` | backlog, or ready with `Queue: ready` |
| in progress | `[~]` | `in_progress` | in_progress |
| blocked | `[!]` | `blocked` | blocked |
| done | `[x]` in the log | `done` | done |
| cancelled | `[-]` in the log | `cancelled` | cancelled |

An item's **kind** says who can act on it: `task` (work you can do), `decision` (a choice a person
must make), `waiting` (something someone else owes) or `later` (not now). An item without a kind
is unclassified; tadu never guesses one. Three dates stay apart: `Due:` is the deadline,
`Check on:` the day to look at the item again, `Not before:` the day before which it cannot
start.

Format 1 items may also carry `ID:`, `Priority:`, `Assignees:`, `Labels:`, `Queue:` and
`Estimate:`. Format 2 tasks have category, type, milestone, relations (`blocked_by`, `parent`,
`related`, ...), notes and acceptance criteria. The specs have every field and rule.

## Commands

| | Command | Does |
| - | ------- | ---- |
| **Set up** | `tadu init` | start a backlog (`--format 2` for task files) |
| | `tadu sync` | write or update the agent rule block in `AGENTS.md` or `CLAUDE.md` |
| | `tadu migrate` | convert format 1 to format 2 |
| **Read** | `tadu list` | items as lines or JSON, with filters for agents |
| | `tadu show KEY` | one item, with the relations pointing at it; `--history` adds its git history, filtered by field, day or author |
| | `tadu changes` | what changed across the backlog in a range of days, for a retro: closed, reopened, started, by whom |
| | `tadu next` | what an agent can do now without a person |
| | `tadu inbox` | what waits on a person: decisions, due follow-ups and checks, blocked tasks |
| | `tadu urgent` | what is urgent, high priority or due soon, by who has to act |
| | `tadu ready` | open items nothing blocks or defers |
| | `tadu similar TEXT` | existing items like a new one, to check before adding |
| | `tadu feed` | recently closed items as JSON |
| **Write** | `tadu add` | a new item or task |
| | `tadu mark` | an item's state (blocked, open, in progress) or fields |
| | `tadu close` | close an item with its evidence or resolution |
| | `tadu set`, `tadu claim` | change a task's own keys (format 2); take an item |
| **Maintain** | `tadu doctor` | check repositories against their format; never writes |
| | `tadu archive`, `tadu fmt` | archive old closed tasks; rewrite task files canonically (format 2) |
| **Integrate** | `tadu mcp` | serve the commands as MCP tools: reading ones, or all with `--allow write` |
| | `tadu hook claude` | run `doctor` after a Claude Code agent edits the backlog |
| | `tadu board` | a kanban page for a workspace: read-only, or `--allow write` to change items |

All commands share a few rules: anything that writes is a dry run until `--write`; every command
takes repository paths (default `.`) or `--workspace DIR`, and `--repository KEY` for one of
them; reading commands take `--json`; exit status `2` means the command refused and wrote
nothing. Each is also an MCP tool and a board call with the same arguments. The [command reference](https://github.com/syntopica/tadu/blob/main/docs/commands.md) has every
option.

## Guides

### Let an agent work alone

```bash
tadu next                  # the agent's work: tasks it can do without a person
tadu inbox --person ana    # when Ana is back: decisions, follow-ups, blocked tasks
tadu urgent                # what is urgent or due, grouped by who acts
```

When the agent meets a question only a person can answer, it records the question, blocks the
task it holds up, and goes on with the next one:

```bash
tadu add --title "Raise the acquirer limit or split large charges" --kind decision --write
tadu mark --match "Accept charges over 10,000 EUR" --state blocked \
  --note 'Blocked on the decision "Raise the acquirer limit or split large charges".' --write
```

`tadu inbox` shows the decision to the person; once it is closed, `tadu mark --state open`
reopens the task. `mark`, `claim` and `close` work the same on both formats, and take an item's
key (`--id`) as well as text from its title. See [next, inbox, urgent](https://github.com/syntopica/tadu/blob/main/docs/commands.md#next-inbox-urgent).

### Close work with proof

```bash
tadu close --match "Fix the header" --evidence "tests/test_header.py passes" --result "The logo shows again" --write
```

```text
- [x] 2026-10-19 — **Frontend:** Fix the header
  - Result: The logo shows again
  - Evidence: tests/test_header.py passes
```

The item moves from `TODO.md` into `TODO_LOG.md` under its year and month, or on a task backlog
from `todo/open/` to `todo/closed/`. A close `doctor` would reject is refused. See
[close](https://github.com/syntopica/tadu/blob/main/docs/commands.md#close).

### See an item's history

```bash
tadu show t-7555ee64 --history --field state
```

```text
2026-11-18 05:21  35857cd4fc  Ana  Close the webhook fix
  state: in_progress → done

2026-11-18 05:21  dc0244ad55  Ana  Start the webhook fix
  state: pending → in_progress

2026-11-18 05:20  0b1f6c2a9e  Ana  Add the webhook fix
  created in TODO.md
  state: pending
```

After the item itself, every change git recorded to it, newest first: here only its state, as
`--field` asks; without it, every field that changed and the lines added or removed. An item is
followed when it is closed, archived, retitled or migrated to a task file; merges and uncommitted
changes show too. `--since`, `--until` and `--author` narrow it as well, on the command line, over
MCP or in the board. See [show --history](https://github.com/syntopica/tadu/blob/main/docs/commands.md#history).

### Run a retro

```bash
tadu changes                                  # the last 14 days
tadu changes --since 2026-11-01 --until 2026-11-30 --event closed,reopened
```

```text
tadu changes: 2026-11-01 to 2026-11-30 · 2 changes

Closed (1) · Ana 1
  2026-11-05  Ana  shop:t-3f2a1b4c  Ship the export.

Reopened (1) · Bob 1
  2026-11-06  Bob  shop:t-3f2a1b4c  Ship the export.  (state: done → pending)
```

Every change git recorded in those days, grouped by kind (closed, cancelled, reopened, started,
blocked, created, changed, removed) with who made them; `--author`, `--field` and `--json`
narrow and shape it. The board's Changes view and the MCP `changes` tool show the same. See
[changes](https://github.com/syntopica/tadu/blob/main/docs/commands.md#changes).

### Move to task files

```bash
tadu migrate --write       # TODO.md, TODO_LOG.md and archived years become todo/*.json
tadu add --title "Reject duplicate webhook deliveries" --category billing --type bug --priority high --write
tadu claim t-8c41d2e7 --as agent:claude --write
tadu set t-8c41d2e7 due=2026-11-20 "labels+=webhooks" --write
tadu close --id t-8c41d2e7 --evidence "pnpm test -- webhook-idempotency passes" --write
```

Work through the commands, never by editing the JSON by hand. See [migrate](https://github.com/syntopica/tadu/blob/main/docs/commands.md#migrate)
and the [format 2 spec](https://github.com/syntopica/tadu/blob/main/spec/todo-format-v2.md).

### Work across repositories

A workspace is a `tadu-workspace.toml` listing repositories and people, plus an untracked
`tadu-workspace.local.toml` saying where each is checked out. Every command then takes
`--workspace DIR`, and `tadu board --workspace DIR` serves a kanban page with Next, Urgent,
Changes and Doctor views, where an item's detail also shows its history and relations. With
`--allow write` the page changes items too: buttons in the detail, drag and drop between
columns, and New item, each previewed first; a repository can stay read-only with
`access = "read"`. See
[Workspaces and the board](https://github.com/syntopica/tadu/blob/main/docs/workspace-and-board.md).

### Check every commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/syntopica/tadu
    rev: <tag or commit>
    hooks:
      - id: tadu-doctor
```

Or in CI: `uvx tadu@<version> doctor .`. Only errors fail; warnings such as an outdated rule block
do not. For Claude Code, the [hook](https://github.com/syntopica/tadu/blob/main/docs/agents.md#claude-code-hook) hands `doctor` errors back to
the agent right after its edit. See [Checking a backlog](https://github.com/syntopica/tadu/blob/main/docs/doctor.md).

## Documentation

| | |
| - | - |
| [Command reference](https://github.com/syntopica/tadu/blob/main/docs/commands.md) | every command and option, exit statuses, environment variables |
| [Checking a backlog](https://github.com/syntopica/tadu/blob/main/docs/doctor.md) | `tadu doctor`, the log check, pre-commit and CI, every finding code |
| [Working with agents](https://github.com/syntopica/tadu/blob/main/docs/agents.md) | the rule block, the MCP server, the Claude Code hook, the skills |
| [Workspaces and the board](https://github.com/syntopica/tadu/blob/main/docs/workspace-and-board.md) | several repositories as one backlog, and the kanban page |
| [Format 1 spec](https://github.com/syntopica/tadu/blob/main/spec/todo-format-v1.md) | `TODO.md`, `TODO_LOG.md`, item fields and kinds, workspaces, the history index |
| [Format 2 spec](https://github.com/syntopica/tadu/blob/main/spec/todo-format-v2.md) | task files, `tadu.json`, relations, ids ([task](https://github.com/syntopica/tadu/blob/main/spec/task.v2.schema.json) and [config](https://github.com/syntopica/tadu/blob/main/spec/config.v2.schema.json) JSON schemas) |
| [Format study](https://github.com/syntopica/tadu/blob/main/bench/format-study/REPORT.md) | the measurements behind format 2 |
| [Changelog](https://github.com/syntopica/tadu/blob/main/CHANGELOG.md) | what changed in each release |

## Development

tadu uses [uv](https://docs.astral.sh/uv/) for development, and [Node.js](https://nodejs.org)
with npm for the checks that run on it; the package itself has no runtime dependencies.

```bash
git clone https://github.com/syntopica/tadu && cd tadu
uv sync                          # the package and the Python quality tools
npm ci                           # jscpd, axe-core, jsdom, puppeteer-core and a Chromium (package.json)
uv run pytest                    # the test suite, one worker per CPU core
uv run pytest -m browser         # the board in jsdom (axe-core) and in Chromium (npm run browser)
uv run codeality-py gate         # every Python check: ruff, mypy, structural rules, deptry, pip-audit, tests
```

The gate is what a change must pass:

| Check | Command | Requires |
| ----- | ------- | -------- |
| Lint and format | `uv run ruff check . && uv run ruff format --check tadu tests` | the rules in `ruff.toml` |
| Types | `uv run mypy tadu tests` | strict mode (`mypy.ini`) |
| Structure | `uv run codeality-py check` | one function or class per module, named after it, and short files (limits in `codeality-py.toml`) |
| Tests | `uv run pytest --cov=tadu` | 100% line and branch coverage |
| Duplicated code | `npm run duplicates` (also a test) | no clone [jscpd](https://github.com/kucherenko/jscpd) finds anywhere in the repository (`.jscpd.json`) |
| Accessibility | `uv run pytest -m browser` | no violation [axe-core](https://github.com/dequelabs/axe-core) finds in any state of the board page, and WCAG AA contrast for every text colour in both themes (`tests/test_board_contrast.py`, part of the suite) |
| The board in a browser | `uv run pytest -m browser` | in Chromium, no console error and no failed request while it blocks an item, drags a card, adds an item and shows every view, light and dark, on a desktop and a phone; no horizontal overflow on the phone |

Layout:

```text
tadu/           the package: one module per function, named after it (run_show.py, card_history.py, ...)
tadu/board/     the board page: plain ES modules, HTML and CSS, no build step
tests/          test_<module>.py for the package's modules, plus shared helpers (git_repo.py, sample_task.py, ...)
spec/           the format specs and JSON schemas
docs/           user documentation
bench/          the format study and benchmark scripts
todo/           tadu's own backlog, in format 2
```

Tests run in parallel ([pytest-xdist](https://pytest-xdist.readthedocs.io), `-n auto` in
`pyproject.toml`), each in its own temporary directories and real git repositories, never against
your configuration; `uv run pytest -n0` runs them in one process, as debugging with `--pdb` needs.
The board's scripts are tested with Node.js when it is installed (those tests are skipped
otherwise): pure functions directly, and the page's elements on a small fake DOM
(`tests/fake_dom.py`), so no browser is needed. The accessibility audit loads the whole page in
jsdom against a real board server, goes through every view, the detail, the filters and the
change dialog, and runs axe-core on each. A second test drives the page in a real Chromium
(`tests/board_browser.mjs`, with [puppeteer-core](https://pptr.dev)): the Chromium that
`@sparticuz/chromium` unpacks on Linux, or the one `CHROME_PATH` names. With
`TADU_SCREENSHOTS=DIR` it also saves a screenshot of each step and view there, for a look at
the page's layout. Both are marked `browser` and left out of the default run because they take
several seconds. The duplication check scans every file of the repository
that `.gitignore` does not leave out, except the format study's frozen results and draft (`bench/format-study/results/`
and `proposal/`) and the test fixtures; it and the audit are skipped until `npm ci` has run.
The project keeps its own backlog with tadu: see `tadu list --open` in a checkout.

## License

[MIT](https://github.com/syntopica/tadu/blob/main/LICENSE)
