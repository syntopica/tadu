"""The repository a proposal changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class ProposalTarget:
    """The workspace key and the GitHub `owner/name` of the repository.

    Also the backlog's folder in the repository and its directory in the server's checkout.
    """

    key: str
    name: str
    backlog: str
    source: Path
