from pathlib import Path

from tadu.unreadable_file_error import UnreadableFileError


def test_message_names_the_file_and_the_reason() -> None:
    error = UnreadableFileError(Path("TODO.md"), "not valid UTF-8")
    assert str(error) == "TODO.md could not be read: not valid UTF-8"
    assert error.path == Path("TODO.md")
    assert error.reason == "not valid UTF-8"
