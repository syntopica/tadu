"""Run a tadu command line in-process and keep what it prints."""

from __future__ import annotations

import contextlib
import io
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

INTERNAL_ERROR = 70


def captured_run(main: Callable[[list[str]], int], argv: list[str]) -> tuple[int, str, str]:
    """(exit status, standard output, standard error); argparse exits become 2.

    A command that fails with an unexpected exception exits INTERNAL_ERROR with its traceback
    as errors, so a server (MCP, the board) answers the call instead of stopping.
    """
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as stop:
            code = stop.code if isinstance(stop.code, int) else 2
        except Exception:  # noqa: BLE001 - any failure of the command is reported, not raised
            code = INTERNAL_ERROR
            name = f"tadu {argv[0]}" if argv else "tadu"
            err.write(f"{name}: internal error\n{traceback.format_exc()}")
    return code, out.getvalue(), err.getvalue()
