from tadu.dependency import Dependency
from tadu.dependency_json import dependency_json


def test_open_target() -> None:
    assert dependency_json(Dependency("t-1", "shop", "!", "blocked")) == {
        "id": "t-1",
        "repository": "shop",
        "state": "!",
        "column": "blocked",
        "open": True,
    }


def test_closed_target() -> None:
    assert dependency_json(Dependency("t-1", "shop", "x", "done"))["open"] is False


def test_missing_target_is_null() -> None:
    data = dependency_json(Dependency("t-1", None, None, None))
    assert (data["repository"], data["state"], data["open"]) == (None, None, None)
