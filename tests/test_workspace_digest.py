import hashlib
from pathlib import Path

from tadu.workspace_digest import workspace_digest


def test_digest_of_the_resolved_path(tmp_path: Path) -> None:
    expected = hashlib.sha256(str(tmp_path.resolve()).encode()).hexdigest()
    assert workspace_digest(tmp_path) == expected
    assert workspace_digest(str(tmp_path / "sub" / "..")) == expected
