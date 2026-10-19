from tadu.introduced_errors import introduced_errors

LOG = "# Log\n\n<!-- tadu:log v1 since 2026-10-01 -->\n"


def test_new_errors_are_listed() -> None:
    after_log = LOG + "\n- [x] 2026-10-19 — a\n"
    assert introduced_errors(("- [ ] a\n", LOG), ("# TODO\n", after_log)) == ["L002"]


def test_existing_errors_are_not_counted_again() -> None:
    texts = ("- [x] old\n", LOG)
    assert introduced_errors(texts, texts) == []
