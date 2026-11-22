"""The commands an agent works a backlog with, for its format."""

from __future__ import annotations


def prime_workflow(*, tasks: bool) -> tuple[str, ...]:
    """One line per step of the workflow, for a task backlog (format 2) or TODO.md (format 1).

    Every command is a dry run until `--write`.
    """
    if tasks:
        return (
            (
                'Before adding work: `tadu similar "<title>"`, then `tadu add` with a category, '
                "type and priority."
            ),
            "Before starting a task: `tadu claim ID --as agent:<name> --write`.",
            'When it is done and verified: `tadu close --id ID --evidence "<proof>" --write`.',
            (
                "A question only a person can answer: `tadu add --kind decision`, then "
                '`tadu set ID "blocked_by+=<decision id>" --write` on the task it holds up.'
            ),
            "Never edit the files under todo/ by hand; run `tadu doctor .` before committing.",
        )
    return (
        'Before adding work: `tadu similar "<title>"`, then `tadu add` into TODO.md.',
        'When it is done and verified: `tadu close --match "<text>" --evidence "<proof>" --write`.',
        (
            "A question only a person can answer: `tadu add --kind decision`, then "
            "`tadu mark` the task it holds up blocked."
        ),
        "Run `tadu doctor .` before committing.",
    )
