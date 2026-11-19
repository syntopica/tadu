"""No backlog, however broken, makes a read command crash: it reports, it never raises.

hypothesis builds TODO.md/TODO_LOG.md files and todo/ task folders from real and broken
pieces; a traceback from any command is a failure. `--hypothesis-profile=thorough` searches
longer (runs of 1,500 and 700 examples found nothing).
"""

import contextlib
import copy
import io
import json
import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tadu.cli import main

ROOT = Path(__file__).parent.parent
LINES = st.sampled_from(
    [
        "# TODO",
        "## Auth",
        "- [ ] Fix the login",
        "- [~] Doing it",
        "- [!] Blocked on vendor",
        "- [x] Done thing",
        "- [-] Dropped",
        "- [?] weird",
        "-[ ] no space",
        "- [ ]",
        "  Priority: high",
        "  Priority: ultra",
        "  Due: 2026-02-30",
        "  Assignees: ana, , bo",
        "  Kind: nope",
        "  ID:",
        "  Check on: 2026-13-01",
        "  Estimate: -1",
        "  Blocked by: k-0001",
        "```",
        "~~~",
        "  ```",
        "\t- [ ] tab item",
        "  - [ ] nested",
        "<!-- tadu:log v1 since 2026-01-01 -->",
        "## 2026",
        "### 2026-11-04",
        "- [x] 2026-11-04 Closed it",
        "  Evidence: CI green",
        "- [x] 2026-99-99 bad",
        "",
        "Ünïcödé ✓ 漢字",
        "\u2028",
        "- [ ] **Auth:** bold title",
        "> quote",
    ]
)
TEXTS = st.lists(LINES, max_size=20).map("\n".join) | st.text(max_size=200)
# Each example runs every read command: a seventh of the profile's examples (14 by default,
# 285 with --hypothesis-profile=thorough).
EXAMPLES = max(5, settings().max_examples // 7)
READS = (
    ["list", "--limit", "0", "--history"],
    ["doctor"],
    ["next"],
    ["inbox"],
    ["urgent"],
    ["feed"],
)
TASKS = [json.loads(p.read_text()) for p in sorted((ROOT / "todo").glob("*/*.json"))]
VALUES: st.SearchStrategy[object] = st.sampled_from(
    [
        None,
        True,
        -1,
        10**12,
        "",
        "x",
        [],
        {},
        ["a b"],
        "2026-02-30",
        "t-0",
        "blocked",
        "done",
        "agent:x",
    ]
)


def run_all(directory: str, commands: list[list[str]]) -> None:
    for command in commands:
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
            contextlib.suppress(SystemExit),
        ):
            main([command[0], directory, *command[1:]])


@settings(max_examples=EXAMPLES)
@given(TEXTS, TEXTS, st.sampled_from(["\n", "\r\n", "\r"]))
def test_any_markdown_backlog(todo: str, log: str, newline: str) -> None:  # type: ignore[misc]  # hypothesis's given is typed with Any
    with tempfile.TemporaryDirectory() as directory:
        for name, text in (("TODO.md", todo), ("TODO_LOG.md", log)):
            Path(directory, name).write_text(text.replace("\n", newline), newline="")
        run_all(directory, [*map(list, READS)])


@settings(max_examples=EXAMPLES)
@given(
    st.lists(
        st.tuples(
            st.sampled_from(TASKS),
            st.lists(
                st.tuples(st.sampled_from(sorted({k for t in TASKS for k in t})), VALUES),
                max_size=3,
            ),
            st.booleans(),
        ),
        min_size=1,
        max_size=5,
    )
)
def test_any_task_backlog(  # type: ignore[misc]  # hypothesis's given is typed with Any
    tasks: list[tuple[dict[str, object], list[tuple[str, object]], bool]],
) -> None:
    with tempfile.TemporaryDirectory() as directory:
        todo = Path(directory, "todo")
        (todo / "open").mkdir(parents=True)
        (todo / "tadu.json").write_text((ROOT / "todo" / "tadu.json").read_text())
        for number, (base, changes, broken) in enumerate(tasks):
            task = copy.deepcopy(base) | dict(changes)
            text = json.dumps(task)
            (todo / "open" / f"t-{number}.json").write_text(text[:-3] if broken else text)
        run_all(directory, [["list", "--limit", "0"], ["doctor"], ["ready"], ["next"], ["fmt"]])
