"""Stop a tadu command before each of its filesystem changes, and check what is left."""

import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from crash_snapshot import Snapshot, known_ids, snapshot, state_of

from tadu.cli import main

INJECT = Path(__file__).with_name("crash_inject.py")
STOPPED = {"SIGKILL": (-9,), "SIGINT": (-2, 130)}


@dataclass(frozen=True)
class Scenario:
    """A fixture, the command run on it, and what may differ from the rule.

    `retry` is the command run again after a stop (the same one by default); `evidence` is (the
    first close's proof, the retry's), counted instead of comparing the end state with the
    command's own. Every half-done state must be one doctor tells from the finished one.
    """

    name: str
    setup: Callable[[Path], object]
    argv: Callable[[Path], list[str]]
    retry: Callable[[Path], list[str]] | None = None
    evidence: tuple[str, str] = ("", "")
    needs_git: bool = False


@dataclass(frozen=True)
class Baseline:
    """The fixture, the command and its retry, and the repository before and after a clean run."""

    template: Path
    work: Path
    argv: list[str]
    retry: list[str]
    known: set[str]
    before: Snapshot
    after: Snapshot
    finished: tuple[int, frozenset[str]]


def tadu(
    repo: Path, argv: list[str], *, stop: tuple[int, str] = (0, "SIGKILL"), log: str = ""
) -> int:
    """Run tadu in a process of its own in `repo`.

    `stop` is (the change to stop before, 0 for none; the signal to stop it with).
    """
    before, signal_name = stop
    environment = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            filter(None, (str(INJECT.parent.parent), os.environ.get("PYTHONPATH")))
        ),
        "CRASH_ROOT": str(repo),
        "CRASH_BEFORE": str(before),
        "CRASH_SIGNAL": signal_name,
        **({"CRASH_LOG": log} if log else {}),
    }
    done = subprocess.run(  # noqa: S603 - this interpreter, the injector of this suite
        [sys.executable, str(INJECT), *argv],
        cwd=repo,
        env=environment,
        capture_output=True,
        check=False,
    )
    return done.returncode


def quiet(repo: Path, argv: list[str]) -> tuple[int, str]:
    """Run tadu in this process in `repo`, keeping its output: (exit status, standard output)."""
    out = io.StringIO()
    with (
        contextlib.chdir(repo),
        contextlib.redirect_stdout(out),
        contextlib.redirect_stderr(io.StringIO()),
    ):
        return main(argv), out.getvalue()


def doctor(repo: Path) -> tuple[int, frozenset[str]]:
    """doctor's exit status and the codes it reports."""
    status, out = quiet(repo, ["doctor", "."])
    return status, frozenset(re.findall(r"(?:error|warning) ([A-Z]\d{3})", out))


def check(scenario: Scenario, stop: str, work: Path) -> tuple[list[str], int]:
    """(every problem found, the number of stops) for the scenario stopped with `stop`."""
    template = work / "template"
    template.mkdir()
    scenario.setup(template)
    known = known_ids(template)
    argv = scenario.argv(template)
    clean = work / "clean"
    shutil.copytree(template, clean, symlinks=True)
    log = work / "steps.log"
    tadu(clean, argv, log=str(log))
    steps = log.read_text().splitlines() if log.exists() else []
    base = Baseline(
        template,
        work,
        argv,
        scenario.retry(template) if scenario.retry else argv,
        known,
        snapshot(template, known)[0],
        snapshot(clean, known)[0],
        doctor(clean),
    )
    problems: list[str] = []
    for number, step in enumerate(steps, start=1):
        where = f"{scenario.name}, stopped before {number} ({step})"
        problems += [f"{where}{problem}" for problem in stopped(scenario, base, (number, stop))]
    return problems, len(steps)


def stopped(scenario: Scenario, base: Baseline, stop: tuple[int, str]) -> list[str]:
    """What is wrong once the command is stopped (before change, signal), and once run again."""
    repo = base.work / f"stop{stop[0]}"
    shutil.copytree(base.template, repo, symlinks=True)
    problems = [] if tadu(repo, base.argv, stop=stop) in STOPPED[stop[1]] else [": not stopped"]
    files, stray = snapshot(repo, base.known)
    state, found = state_of(files, base.before, base.after), doctor(repo)
    if stray and "I001" not in found[1]:
        problems.append(f": {stray} left and doctor says nothing")
    if state == "partial" and found == base.finished:
        problems.append(": half done and doctor says what it says when done")
    if state == "complete" and not stray:
        return problems
    then = time.time() - 180  # the retry comes minutes later: the temporary files are stale
    for path in repo.rglob("*.tmp"):
        os.utime(path, (then, then))
    quiet(repo, base.retry)
    end = snapshot(repo, base.known)
    problems += [f", then run again: {problem}" for problem in ended(scenario, state, end, base)]
    if not scenario.evidence[0] and doctor(repo) != base.finished:
        problems.append(f", then run again: doctor says {doctor(repo)}, not {base.finished}")
    return problems


def ended(
    scenario: Scenario, state: str, end: tuple[Snapshot, list[str]], base: Baseline
) -> list[str]:
    """What is wrong with the end state (files, stray files) of a run again after a stop."""
    files, stray = end
    if stray:
        return [f"{stray} left"]
    first, second = scenario.evidence
    if not first:
        return [] if files == base.after else ["does not end as the command does"]
    text = "".join(files.values())
    expected = (1 if state == "partial" else 0, 1)
    counted = (text.count(first), text.count(second))
    return [] if counted == expected else [f"evidence counted {counted}, not {expected}"]
