from tadu.item_content_line import item_content_line


def test_strips_one_content_indent() -> None:
    assert item_content_line("    ```") == "  ```"
    assert item_content_line("\t  x") == "  x"
    assert item_content_line(" x") == " x"
