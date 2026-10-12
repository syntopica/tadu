from tadu.fresh_todo_text import fresh_todo_text
from tadu.has_state_legend import has_state_legend


def test_backlog_has_a_title_and_the_state_legend() -> None:
    text = fresh_todo_text()
    assert text.startswith("# TODO\n")
    assert has_state_legend(text)


def test_backlog_does_not_claim_a_history_audit() -> None:
    assert "conversation history" not in fresh_todo_text()
