from tadu.payload_text import payload_text


def test_nested_string() -> None:
    assert payload_text({"a": {"b": "x"}}, "a", "b") == "x"


def test_missing_or_not_text_is_empty() -> None:
    assert payload_text({"a": {"b": 3}}, "a", "b") == ""
    assert payload_text({"a": "x"}, "a", "b") == ""
    assert payload_text([], "a") == ""
