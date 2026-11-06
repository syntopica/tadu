import sys
from pathlib import Path

import pytest

from tadu.silence_stdout import silence_stdout


def test_stdout_descriptor_points_at_null_device(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with (tmp_path / "out").open("w") as target:
        monkeypatch.setattr(sys, "stdout", target)
        silence_stdout()
        print("discarded", file=target, flush=True)
    assert (tmp_path / "out").read_text() == ""
