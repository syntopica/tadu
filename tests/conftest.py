from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def private_item_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path_factory: pytest.TempPathFactory
) -> Path:
    """Every test gets its own item cache directory, never the user's ~/.cache."""
    directory = tmp_path_factory.mktemp("cache")
    monkeypatch.setenv("TADU_CACHE_DIR", str(directory))
    monkeypatch.delenv("TADU_NO_CACHE", raising=False)
    return directory
