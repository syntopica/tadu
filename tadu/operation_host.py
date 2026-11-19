"""What a server runs tool calls with."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from tadu.scope import Scope


@dataclass(frozen=True)
class OperationHost:
    """The server's scope, the access level it was started with, and the tadu command line."""

    scope: Scope
    allow: str
    main: Callable[[list[str]], int]
