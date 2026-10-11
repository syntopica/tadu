# tadu

tadu is a backlog format for repositories that coding agents maintain, plus the tools that keep it honest.

- `TODO.md` is the active backlog.
- `TODO_LOG.md` records closed work with its evidence.
- `TODO_HISTORY_INDEX.jsonl` is an optional index of the conversations already reviewed.

The format is specified in [spec/todo-format-v1.md](spec/todo-format-v1.md).

Two commands, both coming in this release:

- `tadu doctor` checks a repository against the format and never writes.
- `tadu sync` updates the marked rule block in an agent instruction file.

## Install

```bash
uv tool install git+https://github.com/syntopica/tadu
```

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
