# Working with agents

tadu is built so that a coding agent keeps the backlog as carefully as a person would. There are
four ways to connect one; use any of them, or all.

| Way | What the agent gets | Set up |
| --- | ------------------- | ------ |
| [The rule block](#the-rule-block) | instructions in `AGENTS.md` or `CLAUDE.md`: how to add, work and close items | `tadu sync . --write` |
| [MCP server](#mcp-server) | the commands as tools it sees without any instruction file | `claude mcp add tadu -- tadu mcp --allow write` |
| [Claude Code hook](#claude-code-hook) | `doctor` errors handed back right after it edits the backlog | one entry in `.claude/settings.json` |
| [Skills](#skills) | `tadu-create` and `tadu-work` | the Claude Code plugin |

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
{ "mcpServers": { "tadu": { "command": "tadu", "args": ["mcp", "--allow", "write"] } } }
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
        "hooks": [{ "type": "command", "command": "tadu hook claude", "timeout": 20 }]
      }
    ]
  }
}
```

## Skills

Two agent skills ship with the format, and the Claude Code plugin also installs the hook above (it
stays silent when `tadu` is not installed):

- `tadu-create` builds `TODO.md`, `TODO_LOG.md` and the history index from the project's agent
  conversation history.
- `tadu-work` executes an existing backlog under an approved plan and run caps.

In Claude Code:

```text
/plugin marketplace add syntopica/tadu
/plugin install tadu@tadu
```

For other agents, copy `skills/<name>/` into the agent's skills directory.
