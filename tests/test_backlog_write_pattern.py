from tadu.backlog_write_pattern import (
    BACKLOG_NAME_PATTERN,
    LEADING_CD_PATTERN,
    SHELL_WRITE_PATTERN,
    TADU_CLOSE_WRITE_PATTERN,
)


def test_backlog_names_and_writes() -> None:
    assert BACKLOG_NAME_PATTERN.search("sed -i '' s/a/b/ TODO_LOG.md")
    assert not BACKLOG_NAME_PATTERN.search("cat README.md")
    assert SHELL_WRITE_PATTERN.search("open('TODO.md','w')")
    assert not SHELL_WRITE_PATTERN.search("grep -n fix TODO.md")


def test_close_with_write_and_leading_cd() -> None:
    assert TADU_CLOSE_WRITE_PATTERN.search("tadu close --match a\n --evidence e --write")
    assert not TADU_CLOSE_WRITE_PATTERN.search("tadu close --match a --evidence e")
    match = LEADING_CD_PATTERN.match("cd ~/repo && tadu close")
    assert match is not None
    assert match.group(1) == "~/repo"
