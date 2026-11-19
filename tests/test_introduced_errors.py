import pytest

from tadu.introduced_errors import introduced_errors

LOG = "# Log\n\n<!-- tadu:log v1 since 2026-10-01 -->\n"


def test_new_errors_are_listed() -> None:
    after_log = LOG + "\n- [x] 2026-10-19 — a\n"
    assert introduced_errors(("- [ ] a\n", LOG), ("# TODO\n", after_log)) == ["L002"]


def test_existing_errors_are_not_counted_again() -> None:
    texts = ("- [x] old\n", LOG)
    assert introduced_errors(texts, texts) == []


LOG_ERROR = "<!-- tadu:log v1 since 2026-01-01 -->\n- [x] 2026-10-19 — no evidence\n"


def test_a_file_left_as_it_was_is_not_checked(monkeypatch: pytest.MonkeyPatch) -> None:
    def no_log_check(_root: object) -> tuple[()]:
        pytest.fail("the unchanged log was checked")

    monkeypatch.setattr("tadu.backlog_errors.check_log_file", no_log_check)
    assert introduced_errors(("# TODO\n", LOG_ERROR), ("# TODO\n- [x] done\n", LOG_ERROR)) == [
        "T003"
    ]
    assert introduced_errors(("# TODO\n", LOG_ERROR), ("# TODO\n- [ ] more\n", LOG_ERROR)) == []


def test_errors_a_changed_log_gains_are_still_found() -> None:
    assert introduced_errors(("# TODO\n", "# Log\n"), ("# TODO\n", LOG_ERROR)) == ["L002"]
    assert introduced_errors(("# TODO\n", LOG_ERROR), ("# TODO\n", LOG_ERROR + "more\n")) == []
