"""Turn the parsed add arguments into a request and run it."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from tadu.add_request import AddRequest
from tadu.add_request_error import add_request_error
from tadu.run_add import run_add

if TYPE_CHECKING:
    import argparse

FIELD_FLAGS = (
    ("Kind", "kind"),
    ("Priority", "priority"),
    ("Assignees", "assignees"),
    ("Due", "due"),
    ("Check on", "check_on"),
    ("Not before", "not_before"),
    ("Labels", "labels"),
    ("Queue", "queue"),
    ("Estimate", "estimate"),
)


def add_command(args: argparse.Namespace) -> int:
    """Refuse invalid values with exit 2; a generated `ID:` comes first unless --no-id.

    Without --kind the item is left unclassified: no `Kind:` line is written.
    """
    uid = None if args.no_id else f"t-{uuid.uuid4()}"
    fields = [("ID", uid)] if uid else []
    fields += [
        (name, str(getattr(args, flag))) for name, flag in FIELD_FLAGS if getattr(args, flag)
    ]
    request = AddRequest(args.title, args.category, tuple(fields), tuple(args.note or ()))
    root = Path(args.path)
    error = add_request_error(request) or (None if root.is_dir() else f"{root}: not a directory")
    if error is not None:
        print(f"tadu add: {error}", file=sys.stderr)
        return 2
    return run_add(root, request, uid or "the item", write=args.write)
