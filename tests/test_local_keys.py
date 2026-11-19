from tadu.config_settings import CONFIG_OPTIONS
from tadu.local_keys import LOCAL_KEYS


def test_local_top_level_keys() -> None:
    own = frozenset({"version", "me", "editor_url", "paths"})
    assert own | {"defaults"} | frozenset(CONFIG_OPTIONS) == LOCAL_KEYS
