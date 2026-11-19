"""What `tadu mcp` tells an agent when it connects."""

from __future__ import annotations

MCP_INSTRUCTIONS = """\
tadu keeps this project's backlog: open work in TODO.md and closed work in TODO_LOG.md, or
(format 2) one JSON file per task under todo/. An item may have a kind: task (work you can
do), decision (a choice a person must make), waiting (someone else owes something) or later
(not now). Due is its deadline, Check on the day to look at it again, Not before the day
before which it cannot start. An item without a kind is unclassified; do not guess one.

- When the user asks what is urgent, call `urgent`.
- When the user asks you to work alone or will be away, call `next` and work through its
  tasks, most pressing first. Never act on a decision, waiting or later item.
- Before adding an item, call `similar` with its title; do not add the same work twice.
- When you reach a question only a person can answer, call `add` with kind `decision` and
  the options and their trade-offs as notes, then `mark` the task it holds up `blocked`
  with a note naming that decision, and go on with the next task instead of waiting or
  guessing.
- When the user is present or asks what is waiting for them, call `inbox`. Once they
  decide, `close` the decision with their answer as its result and `mark` the task it
  held up `open` again.
- When you start a task, `claim` it; when it is done and verified, call `close` with its
  evidence.
- When the user asks what changed, for a retro or a status report, call `changes` (the
  last 14 days unless they name the days); `show` with `history` tells one item's story.
- Name an item by the key `list` or `show` gives (`id`), not by text, when you can.
- Tools that change files take `preview` to see the change first. When a tool named here
  is not offered, the server is read-only (the user starts it with `tadu mcp --allow
  write` to allow changes): tell the user the change you would make instead.
"""
