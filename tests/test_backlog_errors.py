from tadu.backlog_errors import backlog_errors


def test_counts_error_codes_only() -> None:
    errors = backlog_errors("- [x] done\n- [x] done too\n", "- [x] 2026-10-19 — a\n")
    assert errors == {"T003": 2}


def test_clean_backlog_has_none() -> None:
    assert not backlog_errors("# TODO\n\n- [ ] a\n", "# Log\n")


def test_a_text_given_as_none_is_not_checked() -> None:
    assert backlog_errors("- [x] done\n", None) == {"T003": 1}
    log_with_error = "<!-- tadu:log v1 since 2026-01-01 -->\n- [x] 2026-10-19 — no evidence\n"
    assert backlog_errors(None, log_with_error) == {"L002": 1}
    assert backlog_errors(None, None) == {}
