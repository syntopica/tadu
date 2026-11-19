from datetime import date

from tadu.task_places import task_places


def test_open_task() -> None:
    assert task_places("todo/open/t-1.json", None) == ("todo/open/t-1.json", "todo/closed/t-1.json")


def test_closed_task_and_its_archive_folders() -> None:
    assert task_places("app/todo/archive/2025/03/t-1.json", date(2025, 3, 9)) == (
        "app/todo/open/t-1.json",
        "app/todo/closed/t-1.json",
        "app/todo/archive/2025/t-1.json",
        "app/todo/archive/2025/03/t-1.json",
    )


def test_a_file_put_elsewhere_by_hand() -> None:
    assert task_places("todo/archive/2024/t-1.json", date(2025, 3, 9))[-1] == (
        "todo/archive/2024/t-1.json"
    )
