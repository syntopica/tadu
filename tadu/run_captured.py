"""Run a tadu command line in-process and keep what it prints."""

from __future__ import annotations

import contextlib
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


def run_captured(main: Callable[[list[str]], int], argv: list[str]) -> tuple[int, str]:
    """(exit status, standard output followed by standard error); argparse exits become 2."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as stop:
            code = stop.code if isinstance(stop.code, int) else 2
    return code, out.getvalue() + err.getvalue()
