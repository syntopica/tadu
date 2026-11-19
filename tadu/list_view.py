"""The saved view a list call applies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.config_settings import COMMAND_LINE
from tadu.workspace_error import WorkspaceError
from tadu.workspace_view import workspace_view

if TYPE_CHECKING:
    import argparse

    from tadu.card_filter import CardFilter


def list_view(args: argparse.Namespace) -> CardFilter:
    """`--view` of the workspace; WorkspaceError naming the config file that chose it, if one did."""
    try:
        return workspace_view(args.workspace, args.view)
    except WorkspaceError as error:
        source = getattr(args, "option_sources", {}).get("view", COMMAND_LINE)
        if source == COMMAND_LINE:
            raise
        msg = f"{error}; the view comes from {source}"
        raise WorkspaceError(msg) from None
