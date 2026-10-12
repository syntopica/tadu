"""Render one finding for the terminal or as JSON."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.finding import Finding


def format_finding(finding: Finding, *, as_json: bool) -> str:
    """`path:line: severity CODE message`, or one JSON object."""
    if as_json:
        return json.dumps(asdict(finding), sort_keys=True)
    return f"{finding.path}:{finding.line}: {finding.severity} {finding.code} {finding.message}"
