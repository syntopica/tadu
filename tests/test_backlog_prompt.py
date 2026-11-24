import pytest

from tadu.backlog_prompt import backlog_prompt


@pytest.mark.parametrize(
    "prompt",
    [
        "revisa las tareas pendientes",
        "revisa el todo",
        "trabaja en las tareas pendientes",
        "review pending tasks",
        "what is left in the backlog?",
        "show my todos",
        "¿Qué queda pendiente?",
    ],
)
def test_recognizes_backlog_requests(prompt: str) -> None:
    assert backlog_prompt(prompt)


@pytest.mark.parametrize(
    "prompt", ["Fix the login", "review this PR", "haz todo lo necesario", "", "/help"]
)
def test_unrelated_prompts_stay_silent(prompt: str) -> None:
    assert not backlog_prompt(prompt)
