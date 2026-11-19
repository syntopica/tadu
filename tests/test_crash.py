"""Every command that writes, stopped before each filesystem change it makes.

Slow, so not in the default run: `pytest -m crash`. Each stop is a real signal to a real
process: SIGKILL, where no cleanup runs, and SIGINT (Ctrl-C), where it does. After each stop
doctor must tell a half-done state from a finished one, and the same command run again must
end exactly as it does when nothing stops it.
"""

import shutil
import signal
from collections.abc import Callable
from pathlib import Path

import pytest
from crash_fixtures import markdown_split, rich, run, tasks_split
from crash_run import Scenario, check, tadu
from crash_scenarios import SCENARIOS
from old_migration import leftovers

pytestmark = [
    pytest.mark.crash,
    pytest.mark.skipif(not hasattr(signal, "SIGKILL"), reason="needs POSIX signals"),
]
READ_ONLY = (
    ["doctor", "."],
    ["doctor", ".", "--json"],
    ["list", ".", "--json", "--history", "--limit", "0"],
    ["list", ".", "--kind", "decision"],
    ["next", "."],
    ["inbox", "."],
    ["urgent", "."],
    ["ready", "."],
    ["similar", "header", "."],
    ["feed", "."],
)


@pytest.mark.parametrize("stop", ["SIGKILL", "SIGINT"])
@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.name)
def test_a_stopped_command_loses_nothing_and_running_it_again_finishes_it(
    scenario: Scenario, stop: str, tmp_path: Path
) -> None:
    if scenario.needs_git and shutil.which("git") is None:
        pytest.skip("needs git")
    problems, stops = check(scenario, stop, tmp_path)
    assert problems == []
    assert stops > 0 or scenario.name == "recover again after pruning"


def migrated(repo: Path) -> None:
    rich(repo)
    run(repo, "migrate", "--write")


@pytest.mark.parametrize("setup", [markdown_split, tasks_split, leftovers, migrated])
def test_commands_that_read_write_nothing(setup: Callable[[Path], object], tmp_path: Path) -> None:
    setup(tmp_path)
    log = tmp_path.parent / f"{tmp_path.name}.log"
    for argv in READ_ONLY:
        tadu(tmp_path, argv, log=str(log))
        assert not log.exists(), (argv, log.read_text())
