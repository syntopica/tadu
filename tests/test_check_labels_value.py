from tadu.check_labels_value import check_labels_value


def test_slugs_and_non_slugs() -> None:
    assert check_labels_value("shop, ui-kit") is None
    assert check_labels_value("shop, UI") == "Labels holds a value that is not a lowercase slug"
