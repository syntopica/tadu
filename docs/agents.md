# Working with agents

tadu is built so that a coding agent keeps the backlog as carefully as a person would. There are
four ways to connect one; use any of them, or all.

## Codex quick start

Install the CLI and the native plugin:

```bash
uv tool install --force 'git+https://github.com/syntopica/tadu.git'
codex plugin marketplace add https://github.com/syntopica/tadu.git --json
codex plugin add tadu@tadu --json
tadu sync . --write
```

For a local checkout, use its directory instead of the marketplace URL. Review and trust the plugin's two hook commands in Codex, then open a new agent. The plugin bundles a read-only MCP server and the current create, review and work skills; no separate MCP registration or manual skill copy is needed. Disable older standalone copies of the same skills to avoid conflicting guidance.

Ask “review pending tasks” or “revisa las tareas pendientes”. The prompt hook recognizes the backlog request and supplies the equivalent of `tadu prime .`: live counts, at most five next tasks and the workflow. It stays silent for unrelated requests or directories without a backlog. The review skill uses that snapshot directly and queries individual details only when needed. Reviewing does not authorize executing tasks or sending messages.

Without a plugin, start consultation with `tadu prime .`. For a structured inventory use `tadu list --open --json --compact --limit 20`, then `tadu show KEY` for details. Full `list --json` keeps its existing raw-text contract.

The native hooks call `tadu hook codex`. The prompt handler reads only the nearest backlog. The post-tool handler recognizes shell writes and patch headers and reports doctor errors without applying changes. Hooks never call a model or external service. The CLI must remain on Codex's PATH.

The adapter follows the [native hook payload](https://learn.chatgpt.com/docs/hooks#posttooluse): shell tools arrive as `Bash`, and patch text as `apply_patch` with `tool_input.command`. Direct tool argument shapes are accepted for compatibility too.

Native runtime acceptance, after installation and hook trust:

```bash
TADU_TEST_CODEX=1 uv run pytest -n 0 -q tests/test_codex_native.py
```

Set `TADU_CODEX_PROJECT=/absolute/project/path` to check another project. This starts a fresh app server, checks trusted hooks and bundled skills, and calls the read-only MCP `prime` tool in an ephemeral thread. It does not run a model turn. The final conversational acceptance is a new agent receiving the original backlog request.

| Way | What the agent gets | Set up |
| --- | ------------------- | ------ |
| [The rule block](#the-rule-block) | instructions in `AGENTS.md` or `CLAUDE.md`: how to add, work and close items | `tadu sync . --write` |
| [MCP server](#mcp-server) | the commands as tools it sees without any instruction file | `claude mcp add tadu -- tadu mcp --allow write` |
| [Claude Code hook](#claude-code-hook) | `doctor` errors handed back right after it edits the backlog | one entry in `.claude/settings.json` |
| [Skills](#skills)                     | `tadu-create`, `tadu-review` and `tadu-work`                                 | the native Codex or Claude Code plugin          |

## The rule block

`tadu sync` writes the maintenance rule into the repository's instruction file, between marker
lines that `sync` and `doctor` recognize:

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

```bash
tadu sync . --write
tadu sync .
```

```text
AGENTS.md: up to date
```

Contributors need nothing else: the block tells any agent, or any person, how to add an item and
how to log closed work in a shape `doctor` accepts. [`sync`](commands.md#sync) has every option.

The current block is v5. A repository synced with an older one gets an `R004` warning until
`tadu sync . --write` updates it. What earlier versions added:

| Version | Adds |
| ------- | ---- |
| v2 | the closed-entry template, and names the `Evidence:` and `Resolution:` lines the log check requires |
| v3 | `tadu close`, running `tadu doctor .` before committing, and how to install tadu |
| v4 | item kinds; `next`, `inbox`, `urgent`, `add` and `mark`, so an agent working alone records a decision for a person instead of waiting for one; querying the backlog instead of reading it whole; `tadu similar` before adding an item; working a task backlog through its commands |

### Other agents

Most agents already read `AGENTS.md`, so the one block reaches them with no other file. For the
rest, `tadu sync . --agent NAME --write` writes the block into their own file.

| Agent | Reads | Set up |
| ----- | ----- | ------ |
| Codex          | `AGENTS.override.md`, else `AGENTS.md`, else a configured fallback             | `tadu sync . --write`                                                         |
| Claude Code | `CLAUDE.md` (`AGENTS.md` only with its AGENTS.md support enabled) | a `CLAUDE.md` holding `@AGENTS.md`, or `tadu sync . --file CLAUDE.md --write` |
| Gemini CLI | `GEMINI.md`; `AGENTS.md` only when `context.fileName` in its settings names it | `tadu sync . --agent gemini --write` |
| GitHub Copilot | `AGENTS.md` for its agent; `.github/copilot-instructions.md` for every surface | `tadu sync . --agent copilot --write` |
| Cursor | `AGENTS.md`, and the rules under `.cursor/rules/` | nothing; `tadu sync . --agent cursor --write` for a project rule |
| Windsurf | `AGENTS.md` as an always-on rule | `tadu sync . --write` |

Default sync and doctor prefer `AGENTS.override.md`, then `AGENTS.md`, then `CLAUDE.md`. A block already in `CLAUDE.md` does not override that order: Codex does not read its fallback when `AGENTS.md` exists. When both agents use separate files, sync each explicitly; existing content is preserved:

```bash
tadu sync . --file AGENTS.md --write
tadu sync . --file CLAUDE.md --write
```

If `AGENTS.override.md` exists, target it for Codex instead. `doctor` checks the default target; explicit secondary targets need their own `sync --file FILE` check.

A Cursor repository that has both `AGENTS.md` and `.cursor/rules/tadu.mdc` gives the agent the block
twice; keep one. `doctor` checks only `AGENTS.md` or `CLAUDE.md`: after upgrading tadu, run each
`sync --agent` again.

### An agent working alone

An agent takes its work from `tadu next`. When it meets a question only a person can answer, it
records the question with `tadu add --kind decision` and the options as notes, blocks the task
with `tadu mark --state blocked --note` naming the decision, and goes on with the next task.
`tadu inbox` shows the decision when the person is back; once it is closed,
`tadu mark --state open` reopens the task.

## MCP server

`tadu mcp` is a [Model Context Protocol](https://modelcontextprotocol.io) server on standard input
and output, built on no MCP library. An agent connected to it sees the tadu commands as tools, with
their descriptions and a short usage note, so it needs no rule in `AGENTS.md` or `CLAUDE.md` to
know when to use them.

| `--allow` | Tools |
| --------- | ----- |
| `read` (default) | `list`, `show`, `changes`, `ready`, `next`, `inbox`, `urgent`, `similar`, `feed`, `doctor` |
| `write` | also `add`, `close`, `mark`, `set` and `claim` |
| `admin` | also `sync`, `init`, `archive`, `fmt` and `migrate` (marked destructive) |

- Each tool is the command of that name, declared once: its arguments are the command's options
  under the same names (`--due-before` is `due_before`, `--assignee` is `assignees`, a repeatable
  option is a list), with the same choices and help. Common other names are accepted too:
  another spelling of the option (`assignee`, `label`, `as`), a plural (`notes`, `links`,
  `fields`, `events`), `key` for `id` and `id` for `key`; one text given for a list is a list of
  it. A call runs the command itself, so a tool
  answers exactly as the command line does, checks included; a refused call comes back as a tool
  error with the command's message. A change that was written is never a tool error, even when
  `tadu doctor`, run after it, finds errors in the backlog (exit `1`), and neither is doctor's own
  report, so an agent does not make the same change twice. [commands.md](commands.md) has every option.
- The server reads the repository it starts in, the roots it is given, or `--workspace DIR`.
  Every tool takes `repository` to read only one of them; a change writes to exactly one: the
  only one the server reads, or the one `repository` names (the workspace key, the directory name,
  the full path of directories that share a name, or an absolute path). A directory name two
  repositories share and a relative path never choose one; the call fails and lists the
  repositories by full path.
- A tool call runs the command with `--no-config`: [config files](workspace-and-board.md#config-files)
  are ignored, so a tool does what its description says whatever settings a person keeps. The
  server's own `--workspace` can still come from a config file's `[mcp]` table.
- A change writes at once, as the command with `--write`; with `preview` true it only says what
  it would change. Items are named by `id` (the key `list` and `show` give) or `match`.
- A server that does not offer a tool was started read-only. The usage note tells the agent to
  say what it would change instead; start it with `--allow write` to let it change items. A
  repository whose workspace [`access`](workspace-and-board.md#who-may-change-what) is `read`
  stays read-only whatever `--allow` says.

**Claude Code**, for one project:

```bash
claude mcp add tadu -- tadu mcp --allow write
```

or in the project's `.mcp.json`, with `"args": ["mcp", "--workspace", "/path/to/workspace"]` to
serve a workspace (leave out `--allow write` for an agent that should only read):

```json
{
  "mcpServers": {
    "tadu": { "command": "tadu", "args": ["mcp", "--allow", "write"] }
  }
}
```

**Codex**, in `~/.codex/config.toml`:

```toml
[mcp_servers.tadu]
command = "tadu"
args = ["mcp", "--allow", "write"]
```

## Claude Code hook

`tadu hook claude` reads a Claude Code `PostToolUse` event on standard input. When the tool call
changed a backlog file, it runs the doctor checks on that repository and hands any errors back to
the agent as context. It prints nothing otherwise, never blocks the tool call and always exits
`0`.

A backlog change is an `Edit` or `Write` of `TODO.md`, `TODO_LOG.md`, `TODO_HISTORY_INDEX.jsonl`
or a task file under `todo/`; a shell command that writes one; or a `tadu close`, `add`, `mark`,
`set`, `claim`, `archive`, `fmt` or `migrate` run with `--write`. Shell commands are matched as text and
never run.

The [plugin](#skills) installs the hook. Without it, add this to `.claude/settings.json` or
`~/.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|Bash",
        "hooks": [
          { "type": "command", "command": "tadu hook claude", "timeout": 20 }
        ]
      }
    ]
  }
}
```

## Skills

Three agent skills ship with the format, and the Claude Code plugin also installs the hook above (it
stays silent when `tadu` is not installed):

- `tadu-create` builds `TODO.md`, `TODO_LOG.md` and the history index from the project's agent
  conversation history.
- `tadu-review` consults the existing Markdown or task-file backlog without executing it.
- `tadu-work` executes an existing backlog under an approved plan and run caps.

In Claude Code:

```text
/plugin marketplace add syntopica/tadu
/plugin install tadu@tadu
```

For other agents, copy `skills/<name>/` into the agent's skills directory.
