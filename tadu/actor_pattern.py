"""Pattern for who does or records work: a person id, or agent:<name> for an AI agent."""

from __future__ import annotations

import re

ACTOR_PATTERN = re.compile(r"^(agent:)?[a-z0-9][a-z0-9-]*$")
