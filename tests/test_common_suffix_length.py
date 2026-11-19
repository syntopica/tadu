from tadu.common_suffix_length import CHUNK, common_suffix_length


def test_short_texts() -> None:
    assert common_suffix_length("", "", 0) == 0
    assert common_suffix_length("xbc", "ybc", 3) == 2
    assert common_suffix_length("abc", "abc", 3) == 3
    assert common_suffix_length("abc", "abc", 1) == 1
    assert common_suffix_length("abc", "bc", 2) == 2


def test_around_chunk_edges() -> None:
    base = "a" * (3 * CHUNK)
    for at in (0, 1, CHUNK - 1, CHUNK, CHUNK + 1, 2 * CHUNK + 5, 3 * CHUNK - 1):
        spot = len(base) - 1 - at
        changed = base[:spot] + "b" + base[spot + 1 :]
        assert common_suffix_length(base, changed, len(base)) == at, at
    assert common_suffix_length(base, base, len(base)) == len(base)
    assert common_suffix_length(base, base, CHUNK + 7) == CHUNK + 7
