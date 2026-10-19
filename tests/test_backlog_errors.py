from tadu.backlog_errors import backlog_errors


def test_counts_error_codes_only() -> None:
    errors = backlog_errors("- [x] done\n- [x] done too\n", "- [x] 2026-10-19 — a\n")
    assert errors == {"T003": 2}


def test_clean_backlog_has_none() -> None:
    assert not backlog_errors("# TODO\n\n- [ ] a\n", "# Log\n")
