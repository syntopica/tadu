import pytest

from tadu.add_request import AddRequest
from tadu.add_request_error import add_request_error


def request(
    title: str = "T",
    category: str | None = None,
    fields: tuple[tuple[str, str], ...] = (),
    notes: tuple[str, ...] = (),
) -> AddRequest:
    return AddRequest(title, category, fields, notes)


def test_a_plain_request_is_fine() -> None:
    assert add_request_error(request("T", "Billing", (("Kind", "waiting"),), ("Asked.",))) is None


@pytest.mark.parametrize(
    ("bad", "message"),
    [
        (request(" "), "arguments must not be blank"),
        (request(notes=("",)), "arguments must not be blank"),
        (request(category=" "), "arguments must not be blank"),
        (request("a\nb"), "arguments must be single lines"),
        (request(fields=(("Due", "2026-01-01\nx"),)), "arguments must be single lines"),
        (request(category="**B**"), "a category cannot contain *"),
        (request(fields=(("Kind", "soon"),)), "Kind is not one of task, decision, waiting, later"),
        (request(notes=("Due: 2026-01-01",)), "a note cannot start like a field or a list item"),
        (request(notes=("- step",)), "a note cannot start like a field or a list item"),
        (request(notes=("```py",)), "a note cannot open a code fence: ```py"),
    ],
)
def test_refusals(bad: AddRequest, message: str) -> None:
    problem = add_request_error(bad)
    assert problem is not None
    assert problem.startswith(message)
