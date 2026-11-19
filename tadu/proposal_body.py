"""The text of a proposal's pull request or issue."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from tadu.change_diff import change_diff
from tadu.fenced_block import fenced_block

if TYPE_CHECKING:
    from tadu.proposal_request import ProposalRequest


def proposal_body(request: ProposalRequest, *, issue: bool) -> str:
    """What the board tells GitHub's readers: who asked, for what, and the files it changes.

    An issue, which opens where nobody may push, also holds the arguments and the diff that
    whoever may push can apply.
    """
    asked = json.dumps(request.arguments, ensure_ascii=False, sort_keys=True)
    verb = "Requested" if issue else "Proposed"
    lines = [f"{verb} from the tadu board by `{request.login}`: `tadu {request.operation}`.", ""]
    lines += [f"- `{change.path}`" for change in request.changes]
    if issue:
        diff = change_diff(request.changes)
        lines += ["", "Arguments:", fenced_block(asked, "json"), "", fenced_block(diff, "diff")]
    return "\n".join(lines) + "\n"
