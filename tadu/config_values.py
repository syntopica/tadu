"""The options config files give one command."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from tadu.config_layer import config_layer
from tadu.config_settings import NO_DEFAULT_PATH
from tadu.holds_backlog import holds_backlog
from tadu.user_config_file import user_config_file
from tadu.workspace_file_names import LOCAL_FILE

if TYPE_CHECKING:
    import argparse
    from collections.abc import Mapping

    from tadu.config_slot import ConfigSlot


def config_values(
    args: argparse.Namespace, slots: dict[str, ConfigSlot], environ: Mapping[str, str]
) -> dict[str, tuple[object, Path]]:
    """Each option's value and the file it came from: the user's, then the workspace's.

    The local file of the workspace wins. The workspace is the command line's
    `--workspace`, else the user's file's. A command that reads repository paths keeps
    to them when the command line names some, or when it runs in a repository with a
    backlog, which is then its default path: a workspace from the file is dropped, so an
    agent at work in one repository never reads, or is handed, another's items. A view
    from a file goes with it, since a view belongs to a workspace.
    """
    values: dict[str, tuple[object, Path]] = {}
    user = user_config_file(getattr(args, "config", None), environ)
    if user is not None:
        # keys: one option each; the file is the same for all
        values = {
            k: (v, user) for k, v in config_layer(user, args.command, slots, local=False).items()
        }
    here = args.command not in NO_DEFAULT_PATH and holds_backlog(Path())
    if hasattr(args, "paths") and (args.paths or here):
        values.pop("workspace", None)
    workspace = getattr(args, "workspace", values.get("workspace", (None,))[0])
    if workspace is None:
        values.pop("view", None)
    else:
        local = Path(str(workspace)) / LOCAL_FILE
        if local.is_file():
            # keys: one option each; the local file's replace the user's
            values |= {
                k: (v, local)
                for k, v in config_layer(local, args.command, slots, local=True).items()
            }
    return values
