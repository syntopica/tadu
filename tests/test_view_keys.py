from tadu.view_keys import VIEW_KEYS


def test_view_keys_cover_the_list_filters() -> None:
    assert {"name", "due_before", "include_cancelled"} <= VIEW_KEYS
