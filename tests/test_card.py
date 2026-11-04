from card_samples import sample_card


def test_card_holds_values() -> None:
    card = sample_card()
    assert card.column == "backlog"
    assert card.organizations == (("client", "acme"),)
