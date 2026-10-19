from tadu.backlog_file_names import BACKLOG_FILE_NAMES


def test_the_three_backlog_files() -> None:
    assert set(BACKLOG_FILE_NAMES) == {"TODO.md", "TODO_LOG.md", "TODO_HISTORY_INDEX.jsonl"}
