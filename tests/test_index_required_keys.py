from tadu.index_required_keys import INDEX_REQUIRED_KEYS


def test_index_requires_four_keys() -> None:
    assert INDEX_REQUIRED_KEYS == ("source", "conversation_id", "review_status", "review_version")
