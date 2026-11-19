"""print_diff prints a unified diff that turns the old text into the new, found fast.

hypothesis builds pairs of texts; applying the printed diff to the old text, at the line
numbers it names, must give the new one exactly.
"""

import contextlib
import difflib
import io
import re
import time

from hypothesis import given
from hypothesis import strategies as st

from tadu.print_diff import print_diff

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def printed(before: str, after: str) -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        print_diff("TODO.md", before, after)
    return out.getvalue()


def apply(diff: str, before: str) -> str:
    """Patch `before` with a unified diff, checking every context and removed line."""
    old = before.splitlines(keepends=True)
    lines = diff.splitlines(keepends=True)
    result: list[str] = []
    taken = 0
    index = 2 if lines and lines[0].startswith("--- ") else 0
    while index < len(lines):
        match = HUNK.match(lines[index])
        assert match, lines[index]
        start = int(match[1]) - (0 if match[2] == "0" else 1)
        result += old[taken:start]
        taken = start
        index += 1
        while index < len(lines) and not lines[index].startswith("@@"):
            line = lines[index]
            if line[:1] in {" ", "-"}:
                assert old[taken] == line[1:], (taken, line)
                taken += 1
            if line[:1] in {" ", "+"}:
                result.append(line[1:])
            index += 1
    return "".join(result + old[taken:])


LINE = st.sampled_from(
    ["", "- [ ] Fix it", "  Priority: high", "  Due: 2026-01-01", "## Auth", "x", "y"]
)
TEXT = st.lists(LINE, max_size=30).map(lambda lines: "".join(f"{line}\n" for line in lines))


@given(TEXT, TEXT)
def test_the_diff_turns_the_old_text_into_the_new(  # type: ignore[misc]  # hypothesis's given is typed with Any
    before: str, after: str
) -> None:
    diff = printed(before, after).removesuffix("\n")
    assert apply(diff, before) == after


def test_identical_texts_print_nothing_but_a_newline() -> None:
    assert printed("a\nb\n", "a\nb\n") == "\n"


def test_a_small_text_prints_as_difflib_prints_it() -> None:
    before, after = "a\nb\nc\nd\n", "a\nB\nc\nd\ne\n"
    whole = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True), after.splitlines(keepends=True), "TODO.md", "TODO.md"
        )
    )
    assert printed(before, after) == whole + "\n"


def test_one_change_in_a_long_log_is_a_few_lines_found_at_once() -> None:
    entries = [
        f"- [x] 2026-01-{n % 28 + 1:02d} Closed {n}.\n\n  Evidence: ok\n\n" for n in range(25_000)
    ]
    before = "".join(entries)
    after = "".join([*entries[:12_000], "- [x] 2026-02-01 New one.\n\n", *entries[12_000:]])
    started = time.perf_counter()
    diff = printed(before, after)
    assert time.perf_counter() - started < 1.0
    body = diff.splitlines()[3:]
    assert HUNK.match(diff.splitlines()[2])
    assert [line[:1] for line in body].count("+") == 2
    assert [line[:1] for line in body].count("-") == 0
    assert len(body) <= 2 + 2 * 3
    assert apply(diff.removesuffix("\n"), before) == after
