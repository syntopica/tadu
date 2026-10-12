# tadu

tadu is a backlog format for repositories that coding agents maintain, plus the tools that keep it honest.

- `TODO.md` is the active backlog.
- `TODO_LOG.md` records closed work with its evidence.
- `TODO_HISTORY_INDEX.jsonl` is an optional index of the conversations already reviewed.

The format is specified in [spec/todo-format-v1.md](spec/todo-format-v1.md).

Two commands:

- `tadu doctor` checks a repository against the format and never writes.
- `tadu sync` updates the marked rule block in an agent instruction file.

## Requirements

Python 3.12 or newer and [uv](https://docs.astral.sh/uv/). tadu has no runtime dependencies.

## Install

```bash
uv tool install git+https://github.com/syntopica/tadu
tadu --version
```

```text
tadu 0.1.0
```

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

## Write the rule block

`tadu sync` puts the maintenance rule into the repository's instruction file between `<!-- tadu:rule v1 -->` and `<!-- /tadu:rule -->` marker lines. It edits `AGENTS.md`, or `CLAUDE.md` when there is no `AGENTS.md`. Run it without flags first: that prints a diff and changes nothing.

```bash
tadu sync .
```

```text
--- AGENTS.md
+++ AGENTS.md
@@ -1 +1,31 @@
 # Demo
+
+<!-- tadu:rule v1 -->
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

- The write goes to a temporary file in the same directory that then replaces the target, so a failure never leaves a half-written file. Line endings (LF or CRLF) and file mode are kept, and only the text between the markers changes. A block that differs from the current one only in blank lines, as a Markdown formatter such as Prettier leaves it, counts as up to date.
- Markers count only when they are a whole line outside a fenced code block, so quoting them in prose or in an example is safe.
- `--file docs/rules.md` selects another instruction file, given relative to the repository root. `sync` refuses a file that resolves outside the root and exits `2`; it also exits `2` for unbalanced markers and for a file that is not valid UTF-8.
- `--adopt-legacy` replaces an older, unmarked section headed "Continuous TODO" instead of appending a second rule. The section ends at the next Markdown heading of any level, at the next line starting with `<!--`, or at the end of the file. Use it only when that section holds nothing but the standard rule. When it holds repository-specific lines, run plain `tadu sync . --write` and keep those lines by hand under a "TODO conventions specific to this repository" heading after the block.

## Adopt the log check

Closed entries in `TODO_LOG.md` need an `Evidence:` (for `[x]`) or `Resolution:` (for `[-]`) line with content. Without a marker the check is only a warning, so that old history does not fail. A repository adopting the format inserts this line once, after the log header, with the adoption date:

```text
<!-- tadu:log v1 since 2026-10-12 -->
```

Entries dated on or after that day then need proof and a missing line is an error; older entries are legacy and are not checked.

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

Two agent skills ship with the format:

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
