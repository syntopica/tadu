from tadu.visible_repositories import VISIBLE_REPOSITORIES


def test_no_cut_unless_set() -> None:
    assert VISIBLE_REPOSITORIES.get() is None
    token = VISIBLE_REPOSITORIES.set(frozenset({"shop"}))
    try:
        assert VISIBLE_REPOSITORIES.get() == frozenset({"shop"})
    finally:
        VISIBLE_REPOSITORIES.reset(token)
    assert VISIBLE_REPOSITORIES.get() is None
