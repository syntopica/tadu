"""Turn the parsed add arguments into a request and run it."""

from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

from tadu.add_request import AddRequest
from tadu.add_request_error import add_request_error
from tadu.mark_field_values import mark_field_values
from tadu.markdown_add_notes import markdown_add_notes
from tadu.markdown_add_refusal import markdown_add_refusal
from tadu.markdown_add_values import markdown_add_values
from tadu.run_add import run_add


def add_command(args: argparse.Namespace) -> int:
    """Refuse invalid values with exit 2; a generated `ID:` comes first unless --no-id.

    Without --kind the item is left unclassified: no `Kind:` line is written. The options of
    a task backlog are written in their format 1 spelling, or refused (markdown_add_refusal).
    """
    uid = None if args.no_id else f"t-{uuid.uuid4()}"
    fields = [("ID", uid)] if uid else []
    fields += mark_field_values(argparse.Namespace(**{**vars(args), **markdown_add_values(args)}))
    notes = (*(args.note or ()), *markdown_add_notes(args))
    request = AddRequest(args.title, args.category, tuple(fields), notes)
    root = Path(args.path)
    error = (
        markdown_add_refusal(args)
        or add_request_error(request)
        or (None if root.is_dir() else f"{root}: not a directory")
    )
    if error is not None:
        print(f"tadu add: {error}", file=sys.stderr)
        return 2
    return run_add(root, request, uid or "the item", write=args.write)
