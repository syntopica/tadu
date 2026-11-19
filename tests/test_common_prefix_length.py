from tadu.common_prefix_length import CHUNK, common_prefix_length


def test_short_texts() -> None:
    assert common_prefix_length("", "") == 0
    assert common_prefix_length("abc", "abd") == 2
    assert common_prefix_length("abc", "abc") == 3
    assert common_prefix_length("abc", "ab") == 2
    assert common_prefix_length("x", "y") == 0


def test_around_chunk_edges() -> None:
    base = "a" * (3 * CHUNK)
    for at in (0, 1, CHUNK - 1, CHUNK, CHUNK + 1, 2 * CHUNK + 5, 3 * CHUNK - 1):
        changed = base[:at] + "b" + base[at + 1 :]
        assert common_prefix_length(base, changed) == at, at
    assert common_prefix_length(base, base) == 3 * CHUNK
    assert common_prefix_length(base, base[: CHUNK + 3]) == CHUNK + 3
