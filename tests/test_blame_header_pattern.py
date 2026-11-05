from tadu.blame_header_pattern import BLAME_HEADER_PATTERN

SHA = "a" * 40


def test_header_with_and_without_group_count() -> None:
    first = BLAME_HEADER_PATTERN.match(f"{SHA} 1 3 2")
    later = BLAME_HEADER_PATTERN.match(f"{SHA} 2 4")
    assert first is not None
    assert later is not None
    assert (first.group(1), later.group(1)) == ("3", "4")


def test_other_lines() -> None:
    assert BLAME_HEADER_PATTERN.match(f"summary {SHA} 1 2") is None
    assert BLAME_HEADER_PATTERN.match("committer-time 5") is None
