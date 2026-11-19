"""Read file versions from git through two long-running processes."""

from __future__ import annotations

import subprocess
from typing import IO, TYPE_CHECKING, Self, cast

from tadu.git_process import git_process

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType

ABSENT = "0" * 40
REMEMBERED = 8


class BlobReader:
    """`git cat-file` in `root`: object ids by `--batch-check`, texts by `--batch`.

    Names are blob ids or `<commit>:<path>`. A name git does not know, or an all-zero id (an
    absent file), reads as empty text. Texts are kept by blob id, the last REMEMBERED of
    them, so a version unchanged between commits is read once.
    """

    def __init__(self, root: Path) -> None:
        """Start git; HistoryError when it is not installed."""
        self._texts = git_process(root, ("cat-file", "--batch"), subprocess.DEVNULL)
        self._ids = git_process(root, ("cat-file", "--batch-check"), subprocess.DEVNULL)
        self._recent: dict[str, str] = {}

    def __enter__(self) -> Self:
        """The reader itself."""
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Stop git."""
        self._texts.__exit__(kind, error, trace)
        self._ids.__exit__(kind, error, trace)

    def object_id(self, name: str) -> str:
        """The blob id a name resolves to; ABSENT when it names no blob (unknown, or a folder)."""
        if ":" not in name:
            return name
        found = self._ask(self._ids, name)
        return found[0] if found else ABSENT

    def read(self, name: str) -> str:
        """The text of the blob a name resolves to, its lines joined with line feeds."""
        blob = self.object_id(name)
        if not blob.strip("0"):
            return ""
        if blob not in self._recent:
            if len(self._recent) == REMEMBERED:
                del self._recent[next(iter(self._recent))]
            self._recent[blob] = self._fetch(blob)
        return self._recent[blob]

    def _fetch(self, blob: str) -> str:
        """Ask git for one blob's text; empty when git lacks it."""
        found = self._ask(self._texts, blob)
        if found is None:
            return ""
        data = cast("IO[bytes]", self._texts.stdout).read(found[1] + 1)[:-1]
        return "\n".join(data.decode(errors="replace").splitlines())

    @staticmethod
    def _ask(process: subprocess.Popen[bytes], name: str) -> tuple[str, int] | None:
        """Send one name; the blob's id and size, or None: `<name> missing`, or not a blob."""
        ask, answer = cast("IO[bytes]", process.stdin), cast("IO[bytes]", process.stdout)
        ask.write(f"{name}\n".encode())
        ask.flush()
        words = answer.readline().decode(errors="replace").split()
        if (
            len(words) < len(("id", "blob", "size"))
            or words[-2] != "blob"
            or not words[-1].isdigit()
        ):
            return None
        return words[0], int(words[-1])
