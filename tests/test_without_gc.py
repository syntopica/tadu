import gc

import pytest

from tadu.without_gc import without_gc


def test_collection_is_paused_then_restored() -> None:
    assert gc.isenabled()
    assert without_gc(lambda: int(gc.isenabled())) == 0
    assert gc.isenabled()


def test_restored_after_an_error_and_left_off_when_it_was_off() -> None:
    def fail() -> int:
        raise RuntimeError

    with pytest.raises(RuntimeError):
        without_gc(fail)
    assert gc.isenabled()
    gc.disable()
    try:
        without_gc(lambda: 0)
        assert not gc.isenabled()
    finally:
        gc.enable()
