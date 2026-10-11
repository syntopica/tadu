from tadu.has_malformed_rule_markers import has_malformed_rule_markers


def test_no_markers_is_not_malformed() -> None:
    assert not has_malformed_rule_markers("# A\n")


def test_one_open_then_one_close_is_not_malformed() -> None:
    assert not has_malformed_rule_markers("<!-- tadu:rule v1 -->\nx\n<!-- /tadu:rule -->\n")


def test_open_without_close_is_malformed() -> None:
    assert has_malformed_rule_markers("<!-- tadu:rule v1 -->\nx\n")


def test_close_without_open_is_malformed() -> None:
    assert has_malformed_rule_markers("x\n<!-- /tadu:rule -->\n")


def test_two_opens_is_malformed() -> None:
    text = "<!-- tadu:rule v1 -->\n<!-- tadu:rule v1 -->\n<!-- /tadu:rule -->\n"
    assert has_malformed_rule_markers(text)


def test_close_before_open_is_malformed() -> None:
    assert has_malformed_rule_markers("<!-- /tadu:rule -->\n<!-- tadu:rule v1 -->\n")
