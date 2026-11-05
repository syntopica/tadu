from tadu.dependency import Dependency


def test_holds_values() -> None:
    dependency = Dependency("t-1", "shop", "~", "in_progress")
    assert (dependency.repository, dependency.state, dependency.column) == (
        "shop",
        "~",
        "in_progress",
    )
