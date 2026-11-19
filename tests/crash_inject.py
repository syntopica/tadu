"""Run the tadu CLI and stop it right before its k-th filesystem change inside a repository.

Run as a script by crash_run.py, so a real signal stops a real process:

    CRASH_ROOT=dir   only changes under this directory count (cache and scratch files do not)
    CRASH_BEFORE=k   stop before the k-th change; 0 never stops, only records
    CRASH_SIGNAL=S   SIGKILL (no cleanup runs) or SIGINT (Ctrl-C: cleanup runs)
    CRASH_LOG=file   each counted change is appended as "operation<TAB>path below the root"
"""

import builtins
import io
import os
import shutil
import signal
import sys
from pathlib import Path
from typing import Protocol, cast

# os functions that change the filesystem: name, operation logged, position of the path
OS_CHANGES = (
    ("replace", "rename", 1),
    ("rename", "rename", 1),
    ("link", "hardlink", 1),
    ("unlink", "delete", 0),
    ("remove", "delete", 0),
    ("mkdir", "mkdir", 0),
    ("rmdir", "rmdir", 0),
)


class Call(Protocol):
    """Any function: the ones patched here are called as their callers call them."""

    def __call__(self, *args: object, **kwargs: object) -> object: ...


class Counter:
    """Counts the changes under one root, logs them, and stops the process at the chosen one."""

    def __init__(self, root: str, before: int, stop: signal.Signals, log: str | None) -> None:
        self.root, self.before, self.stop, self.log = os.path.realpath(root), before, stop, log
        self.count = self.busy = 0
        self.opened = io.open

    def __call__(self, operation: str, path: object) -> None:
        """Count a change to `path`, if it is under the root and not part of a counted one."""
        if self.busy or not isinstance(path, str | bytes | os.PathLike):
            return
        real = os.path.realpath(os.fsdecode(path))
        if real != self.root and not real.startswith(self.root + os.sep):
            return
        self.count += 1
        if self.log:
            with self.opened(self.log, "a", encoding="utf-8") as handle:
                handle.write(f"{operation}\t{os.path.relpath(real, self.root)}\n")
        if self.count == self.before:
            sys.stdout.flush()
            sys.stderr.flush()
            os.kill(os.getpid(), self.stop)


def counted(step: Counter, real: Call, operation: str, at: int) -> Call:
    """`real`, counting the path at position `at` of each call first."""

    def call(*args: object, **kwargs: object) -> object:
        step(operation, args[at] if len(args) > at else None)
        return real(*args, **kwargs)

    return call


def install(step: Counter) -> None:
    """Count every os, io and shutil call that changes the filesystem."""
    for name, operation, at in OS_CHANGES:
        setattr(os, name, counted(step, getattr(os, name), operation, at))
    os_open, opened, rmtree = (cast("Call", real) for real in (os.open, io.open, shutil.rmtree))

    def counted_os_open(path: object, flags: int, *args: object, **kwargs: object) -> object:
        if flags & os.O_CREAT and not kwargs.get("dir_fd"):
            step("create", path)
        return os_open(path, flags, *args, **kwargs)

    def counted_open(file: object, mode: str = "r", *args: object, **kwargs: object) -> object:
        if set(mode) & set("wax+"):
            step(f"open-{mode}", file)
        return opened(file, mode, *args, **kwargs)

    def counted_rmtree(path: object, *args: object, **kwargs: object) -> object:
        step("rmtree", path)
        step.busy += 1
        try:
            return rmtree(path, *args, **kwargs)
        finally:
            step.busy -= 1

    for owner, name, patched in (
        (os, "open", counted_os_open),
        (builtins, "open", counted_open),
        (io, "open", counted_open),
        (shutil, "rmtree", counted_rmtree),
    ):
        setattr(owner, name, patched)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    install(
        Counter(
            os.environ["CRASH_ROOT"],
            int(os.environ.get("CRASH_BEFORE", "0")),
            getattr(signal, os.environ.get("CRASH_SIGNAL", "SIGKILL")),
            os.environ.get("CRASH_LOG"),
        )
    )
    from tadu.cli import main

    sys.exit(main(sys.argv[1:]))
