from tadu.local_keys import LOCAL_KEYS


def test_local_top_level_keys() -> None:
    assert frozenset({"version", "me", "editor_url", "paths"}) == LOCAL_KEYS
