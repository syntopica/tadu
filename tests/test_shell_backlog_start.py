from pathlib import Path

from tadu.shell_backlog_start import shell_backlog_start


def test_named_targets_win_over_the_start() -> None:
    start = Path("/a")
    assert shell_backlog_start("printf x > /b/TODO.md", start) == Path("/b")
    assert shell_backlog_start("sed -i '' s/x/y/ sub/TODO_LOG.md", start) == Path("/a/sub")
    assert shell_backlog_start("tadu close /c --match x --write", start) == Path("/c")
    assert shell_backlog_start("python3 -c \"open('/d/TODO.md','w')\"", start) == Path("/d")
    assert shell_backlog_start('printf x > "/r s/TODO.md"', start) == Path("/r s")
    assert shell_backlog_start("tadu close '/r s' --match x --write", start) == Path("/r s")
    assert shell_backlog_start("cp /b/TODO.md /e/TODO.md", start) == Path("/e")


def test_bare_names_and_option_first_closes_keep_the_start() -> None:
    start = Path("/a")
    assert shell_backlog_start("printf x >> TODO.md", start) == start
    assert shell_backlog_start("tadu close --match x --write", start) == start
