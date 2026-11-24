---
name: tadu-review
description: Use when the user asks to review pending tasks, see the backlog, find urgent work or understand what is waiting for them. Includes "revisa las tareas pendientes", "revisa el todo", and "what is left in the backlog". Consultation only; use tadu-work when execution is requested.
---

# Review pending work

Use the current repository's Tadu backlog, either `TODO.md` or `todo/tadu.json`. Start with the native prompt's Tadu snapshot when present; it already contains the live `prime` briefing. Otherwise call the MCP `prime` tool or `tadu prime .` once. Do not search for backlog files or read all task documents to discover the format.

Use the smallest follow-up query that answers the request: `urgent` for priorities and deadlines, `inbox` for decisions and follow-ups, `next` for executable work, or `list --open --json --compact --limit 20` for a filtered inventory. Read an individual task with `show` when details matter. Preserve pagination; never request an unlimited full JSON inventory for an initial review.

Report counts, the most pressing tasks, and the next action or blocker. Name tasks by title and state their status in words; keep IDs in tool calls. Distinguish recorded evidence from newly verified external outcomes. A task listed by `next` still needs the user's authority for messages, production writes and other external actions.

A review does not authorize implementing, closing, reclassifying or sending anything. Stay read-only unless the user requests a change. If Tadu is unavailable, report that limitation and use the repository's documented fallback.
