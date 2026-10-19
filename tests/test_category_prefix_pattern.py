from tadu.category_prefix_pattern import CATEGORY_PREFIX_PATTERN


def test_bold_category_prefix() -> None:
    assert CATEGORY_PREFIX_PATTERN.match("**Bugs:** crash")
    assert not CATEGORY_PREFIX_PATTERN.match("**pxpn: waits on a PR.** text")
    assert not CATEGORY_PREFIX_PATTERN.match("plain")
