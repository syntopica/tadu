from tadu.access_allows import access_allows


def test_levels_include_the_ones_below() -> None:
    assert access_allows("read", "read")
    assert not access_allows("read", "write")
    assert access_allows("write", "write")
    assert not access_allows("write", "admin")
    assert access_allows("admin", "read")
    assert not access_allows("admin", "local")
