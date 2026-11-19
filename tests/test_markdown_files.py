from tadu.markdown_files import markdown_files


def test_top_and_nested_backlog() -> None:
    assert markdown_files("TODO_LOG.md") == ("TODO.md", "TODO_LOG.md")
    assert markdown_files("apps/web/TODO.md") == ("apps/web/TODO.md", "apps/web/TODO_LOG.md")


def test_a_year_of_the_log_archive() -> None:
    assert markdown_files("docs/todo-log/2025.md") == (
        "TODO.md",
        "TODO_LOG.md",
        "docs/todo-log/2025.md",
    )
    assert markdown_files("apps/web/docs/todo-log/2025.md") == (
        "apps/web/TODO.md",
        "apps/web/TODO_LOG.md",
        "apps/web/docs/todo-log/2025.md",
    )
