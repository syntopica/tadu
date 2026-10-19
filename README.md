# tadu

tadu is a backlog format for repositories that coding agents maintain, plus the tools that keep it honest.

- `TODO.md` is the active backlog.
- `TODO_LOG.md` records closed work with its evidence.
- `TODO_HISTORY_INDEX.jsonl` is an optional index of the conversations already reviewed.

The format is specified in [spec/todo-format-v1.md](spec/todo-format-v1.md).

Five commands:

- `tadu init` starts the backlog in a repository that has none.
- `tadu doctor` checks a repository against the format and never writes.
- `tadu sync` updates the marked rule block in an agent instruction file.
- `tadu close` moves one finished item from `TODO.md` into `TODO_LOG.md`.
- `tadu hook claude` is a Claude Code hook that runs `doctor` after an agent changes the backlog.

Contributors need none of it: the rule block that `sync` writes into `AGENTS.md` or `CLAUDE.md` tells any agent, or any person, how to add an item and how to log closed work in a shape `doctor` accepts.

## Requirements

Python 3.12 or newer. tadu has no runtime dependencies; [uv](https://docs.astral.sh/uv/) is only needed to work on tadu itself.

## Install

tadu needs Python 3.12 or newer and nothing else. Install it as a command with any Python installer:

```bash
uv tool install git+https://github.com/syntopica/tadu
# or
pipx install git+https://github.com/syntopica/tadu
# or, into the current Python environment
python3 -m pip install git+https://github.com/syntopica/tadu
```

```bash
tadu --version
```

```text
tadu 0.1.0
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

## Write the rule block

`tadu sync` puts the maintenance rule into the repository's instruction file between `<!-- tadu:rule v3 -->` and `<!-- /tadu:rule -->` marker lines. It edits `AGENTS.md`, or `CLAUDE.md` when there is no `AGENTS.md`. Run it without flags first: that prints a diff and changes nothing.

```bash
tadu sync .
```

```text
--- AGENTS.md
+++ AGENTS.md
@@ -1 +1,31 @@
 # Demo
+
+<!-- tadu:rule v3 -->
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

- The write goes to a temporary file in the same directory that then replaces the target, so a failure never leaves a half-written file. Line endings (LF or CRLF) and file mode are kept, and only the text between the markers changes. A block that differs from the current one only in blank lines or soft line wrapping, as a Markdown formatter such as Prettier with `proseWrap` leaves it, counts as up to date; a changed word, list item, heading, hard line break or fenced line is still drift.
- Markers count only when they are a whole line outside a fenced code block, so quoting them in prose or in an example is safe.
- `--file docs/rules.md` selects another instruction file, given relative to the repository root. `sync` refuses a root that is not a directory and a file that resolves outside the root, and exits `2`; it also exits `2` for unbalanced markers and for a file that is not valid UTF-8.
- `--adopt-legacy` replaces an older, unmarked section headed "Continuous TODO" instead of appending a second rule. The section ends at the next Markdown heading of any level, at the next line starting with `<!--`, or at the end of the file. Use it only when that section holds nothing but the standard rule. When it holds repository-specific lines, run plain `tadu sync . --write` and keep those lines by hand under a "TODO conventions specific to this repository" heading after the block.

A repository synced before the current block version gets an `R004` warning; run `tadu sync . --write` to update it. Version 2 added the closed-entry template and names the `Evidence:` and `Resolution:` lines the log check requires; version 3 adds `tadu close`, tells agents to run `tadu doctor .` before committing, and says how to install tadu.

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

Or as a CI step, with the same pin and either runner:

```bash
uvx --from git+https://github.com/syntopica/tadu@<tag or commit> tadu doctor .
pipx run --spec git+https://github.com/syntopica/tadu@<tag or commit> tadu doctor .
```

### After every agent edit, in Claude Code

`tadu hook claude` reads a Claude Code `PostToolUse` event on standard input. When the tool call changed a backlog file (an `Edit` or `Write` of `TODO.md`, `TODO_LOG.md` or `TODO_HISTORY_INDEX.jsonl`, a shell command that writes one, or `tadu close --write`), it runs the doctor checks on that repository and hands any errors back to the agent as context. It prints nothing otherwise, never blocks the tool call and always exits `0`. Shell commands are matched as text and never run.

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
| E001 | error | a file could not be read (not valid UTF-8, or an I/O error) |

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
