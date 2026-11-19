"""How argparse declares one operation argument."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.param_options import param_options

if TYPE_CHECKING:
    from tadu.param import Param

NARGS = {"list": "*", "words": "+"}


def param_arguments(param: Param) -> tuple[tuple[str, ...], dict[str, object]]:
    """The names and keyword arguments of `add_argument` for the parameter.

    A positional list takes any number of values, and words one or more; an optional
    positional takes zero or one. Group membership is left to the caller.
    """
    options = param_options(param)
    if param.positional:
        nargs = NARGS.get(param.kind, None if param.required else "?")
        return (param.name,), options | ({} if nargs is None else {"nargs": nargs})
    if param.required and not param.exclusive:
        options["required"] = True
    return param.flags or (param.flag,), {**options, "dest": param.name}
