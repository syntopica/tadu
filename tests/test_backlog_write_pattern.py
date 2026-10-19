from tadu.backlog_write_pattern import (
    BACKLOG_NAME_PATTERN,
    BACKLOG_PATH_PATTERN,
    LEADING_CD_PATTERN,
    SHELL_WRITE_PATTERN,
    TADU_CLOSE_ROOT_PATTERN,
    TADU_CLOSE_WRITE_PATTERN,
)


def test_backlog_names_and_writes() -> None:
    assert BACKLOG_NAME_PATTERN.search("sed -i '' s/a/b/ TODO_LOG.md")
    assert not BACKLOG_NAME_PATTERN.search("cat README.md")
    assert SHELL_WRITE_PATTERN.search("open('TODO.md','w')")
    assert not SHELL_WRITE_PATTERN.search("grep -n fix TODO.md")
    assert SHELL_WRITE_PATTERN.search("echo x >> 'TODO_LOG.md'")
    assert not SHELL_WRITE_PATTERN.search("cat TODO.md > /dev/null")


def test_close_with_write_and_leading_cd() -> None:
    assert TADU_CLOSE_WRITE_PATTERN.search("tadu close --match a\n --evidence e --write")
    assert not TADU_CLOSE_WRITE_PATTERN.search("tadu close --match a --evidence e")
    match = LEADING_CD_PATTERN.match("cd ~/repo && tadu close")
    assert match is not None
    assert match.group(1) == "~/repo"


def test_backlog_paths_and_close_roots() -> None:
    path = BACKLOG_PATH_PATTERN.search("cp x /r/TODO.md")
    assert path is not None
    assert path.group(1) == "/r/"
    assert not BACKLOG_PATH_PATTERN.search("cp x TODO.md")
    root = TADU_CLOSE_ROOT_PATTERN.search("tadu close ../r --match a")
    assert root is not None
    assert root.group(1) == "../r"
    assert not TADU_CLOSE_ROOT_PATTERN.search("tadu close --match a")
