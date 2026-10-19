from tadu.backlog_write_pattern import (
    BACKLOG_NAME_PATTERN,
    BACKLOG_PATH_PATTERN,
    LEADING_CD_PATTERN,
    SHELL_WRITE_PATTERN,
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


def test_backlog_paths_in_a_word() -> None:
    assert BACKLOG_PATH_PATTERN.findall(">/r s/TODO.md") == ["/r s/"]
    assert BACKLOG_PATH_PATTERN.findall("open('/d/TODO_LOG.md','w')") == ["/d/"]
    assert not BACKLOG_PATH_PATTERN.findall("TODO.md")
