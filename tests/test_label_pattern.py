from tadu.label_pattern import LABEL_PATTERN


def test_lowercase_slug() -> None:
    assert LABEL_PATTERN.match("ui-kit2")
    assert not LABEL_PATTERN.match("-x")
    assert not LABEL_PATTERN.match("Up")
