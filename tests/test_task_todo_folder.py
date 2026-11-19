from tadu.task_todo_folder import task_todo_folder


def test_every_folder_depth() -> None:
    assert task_todo_folder("todo/open/t-1.json") == "todo"
    assert task_todo_folder("apps/web/todo/closed/t-1.json") == "apps/web/todo"
    assert task_todo_folder("todo/archive/2025/t-1.json") == "todo"
    assert task_todo_folder("todo/archive/2025/11/t-1.json") == "todo"
    assert task_todo_folder("elsewhere/t-1.json") == "elsewhere"
