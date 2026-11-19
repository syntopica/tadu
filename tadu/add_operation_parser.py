"""Declare one operation as a subcommand."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.param_arguments import param_arguments
from tadu.target_params import target_params

if TYPE_CHECKING:
    import argparse

    from tadu.intermixed_parser import IntermixedParser
    from tadu.operation import Operation


def add_operation_parser(
    commands: argparse._SubParsersAction[IntermixedParser], operation: Operation
) -> None:
    """Add the operation with its own arguments, then those of its target.

    Positionals keep their order: the operation's (such as a key), then the repository roots.
    Arguments sharing `exclusive` form one mutually exclusive group.
    """
    parser = commands.add_parser(operation.name, help=operation.help)
    groups: dict[str, argparse._ActionsContainer] = {}
    for param in (*operation.params, *target_params(operation)):
        group = param.exclusive or param.section
        if group and group not in groups:
            # keys: one group per name, made the first time the name comes up.
            groups[group] = (
                parser.add_mutually_exclusive_group(required=param.required)
                if param.exclusive
                else parser.add_argument_group(group)
            )
        names, options = param_arguments(param)
        groups.get(group, parser).add_argument(*names, **options)  # type: ignore[arg-type]
