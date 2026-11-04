from dataclasses import replace
from datetime import date

from card_samples import sample_card

from tadu.card_filter import CardFilter
from tadu.card_matches import card_matches


def test_empty_filter_matches() -> None:
    assert card_matches(sample_card(), CardFilter())


def test_project() -> None:
    assert card_matches(sample_card(), CardFilter(project="storefront"))
    assert not card_matches(sample_card(), CardFilter(project="other"))


def test_org_and_role() -> None:
    card = sample_card()
    assert card_matches(card, CardFilter(org="acme"))
    assert not card_matches(card, CardFilter(org="zed"))
    assert card_matches(card, CardFilter(role="client"))
    assert not card_matches(card, CardFilter(role="partner"))
    assert card_matches(card, CardFilter(org="acme", role="client"))
    assert not card_matches(card, CardFilter(org="acme", role="partner"))


def test_org_with_role_needs_same_pair() -> None:
    card = replace(sample_card(), organizations=(("client", "acme"), ("partner", "zed")))
    assert not card_matches(card, CardFilter(org="acme", role="partner"))
    assert card_matches(card, CardFilter(org="zed", role="partner"))


def test_assignee_label_column() -> None:
    card = sample_card()
    assert card_matches(card, CardFilter(assignee="ana"))
    assert not card_matches(card, CardFilter(assignee="bob"))
    assert card_matches(card, CardFilter(label="x"))
    assert not card_matches(card, CardFilter(label="y"))
    assert card_matches(card, CardFilter(column="backlog"))
    assert not card_matches(card, CardFilter(column="done"))


def test_priority() -> None:
    card = sample_card()
    assert card_matches(card, CardFilter(priority="high"))
    assert not card_matches(card, CardFilter(priority="low"))
    bare = replace(card, item=replace(card.item, fields=replace(card.item.fields, priority=None)))
    assert not card_matches(bare, CardFilter(priority="high"))


def test_due_before() -> None:
    card = sample_card()
    assert card_matches(card, CardFilter(due_before=date(2026, 12, 2)))
    assert not card_matches(card, CardFilter(due_before=date(2026, 12, 1)))
    bare = replace(card, item=replace(card.item, fields=replace(card.item.fields, due=None)))
    assert not card_matches(bare, CardFilter(due_before=date(2027, 1, 1)))


def test_cancelled_hidden_unless_requested() -> None:
    card = replace(sample_card(), column="cancelled")
    assert not card_matches(card, CardFilter())
    assert card_matches(card, CardFilter(include_cancelled=True))
    assert card_matches(card, CardFilter(column="cancelled"))
    assert not card_matches(card, CardFilter(column="cancelled", project="other"))
