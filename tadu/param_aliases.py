"""The other names a tool call may give an argument."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tadu.param import Param


def param_aliases(param: Param) -> tuple[str, ...]:
    """Its declared aliases, then the names its command-line flags spell, without its own name.

    `--assignee` and `--assignees` make `assignee` an alias of `assignees`; `--as` makes `as`
    one of `who`.
    """
    spelled = (flag.lstrip("-").replace("-", "_") for flag in param.flags)
    # keys: dict.fromkeys only drops a name given twice, keeping the first.
    return tuple(dict.fromkeys(name for name in (*param.aliases, *spelled) if name != param.name))
