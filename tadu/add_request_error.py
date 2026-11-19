"""Validate a request to add an item before touching any file."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.field_checks import FIELD_CHECKS
from tadu.first_problem import first_problem
from tadu.note_error import note_error
from tadu.text_problem import text_problem

if TYPE_CHECKING:
    from tadu.add_request import AddRequest


def add_request_error(request: AddRequest) -> str | None:
    """The first reason the item cannot be written as asked, or None."""
    texts = [request.title, *request.notes, *(value for _, value in request.fields)]
    texts += [request.category] if request.category is not None else []
    problems = [
        text_problem(texts),
        "a category cannot contain *" if "*" in (request.category or "") else None,
        *(FIELD_CHECKS[name](value.strip()) for name, value in request.fields),
        *(note_error(note) for note in request.notes),
    ]
    return first_problem(problems)
