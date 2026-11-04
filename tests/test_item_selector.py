from tadu.item_selector import ItemSelector


def test_alias_names_the_selector_shape() -> None:
    assert ItemSelector.__name__ == "ItemSelector"
