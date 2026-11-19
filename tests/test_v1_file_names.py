from tadu.v1_file_names import V1_FILES


def test_the_two_markdown_files_of_a_format_1_backlog() -> None:
    assert V1_FILES == ("TODO.md", "TODO_LOG.md")
