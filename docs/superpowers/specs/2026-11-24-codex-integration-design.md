# Codex backlog integration

The owner requested that asking to review pending tasks use Tadu directly, without rediscovering backlog files, loading unrelated workflows, or dumping every task. Ship the integration in this repository and install it locally before a fresh-agent acceptance check.

Use a native Codex plugin with a read-only MCP server, a bounded UserPromptSubmit briefing, a PostToolUse validation hook, and a consultation skill. Keep the existing Claude plugin working. The CLI remains usable without any plugin or provider dependency.

Default instruction discovery must prefer AGENTS.override.md and AGENTS.md over CLAUDE.md, matching Codex. Preserve all existing content and explicit --file behavior. Explain how to sync both agents when both files exist.

Keep full JSON backward compatible; add an explicit compact list projection that omits raw task text. Query details through show. The review hook must recognize the reported Spanish prompts and equivalent English requests, stay silent for unrelated prompts and missing backlogs, never mutate a backlog, and treat task text as data rather than instructions.

Verify regression tests, the repository quality gate, relocated plugin execution, fresh Codex hook/skill/MCP discovery, and the real TienesLaVibra briefing. The owner's next agent supplies the final conversational acceptance check.
