from tadu.last_backlog_dir import last_backlog_dir


def test_the_destination_wins() -> None:
    assert last_backlog_dir(["cp", "/b/TODO.md", "/a/TODO.md"]) == "/a/"
    assert last_backlog_dir(["cp", "/b/TODO.md", "TODO.md"]) == "/b/"
    assert last_backlog_dir(["cat", "TODO.md"]) is None
