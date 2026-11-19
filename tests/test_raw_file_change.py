from tadu.git_file_change import GitFileChange
from tadu.raw_file_change import raw_file_change

A, B, C, Z = "a" * 40, "b" * 40, "c" * 40, "0" * 40


def test_one_parent() -> None:
    raw = f":100644 100644 {A} {B} M"
    assert raw_file_change(raw, "TODO.md") == GitFileChange("TODO.md", (A,), B)


def test_added_file() -> None:
    raw = f":000000 100644 {Z} {B} A"
    assert raw_file_change(raw, "TODO.md") == GitFileChange("TODO.md", (Z,), B)


def test_merge_lists_a_blob_per_parent() -> None:
    raw = f"::100644 100644 100644 {A} {B} {C} MM"
    assert raw_file_change(raw, "TODO.md") == GitFileChange("TODO.md", (A, B), C)
