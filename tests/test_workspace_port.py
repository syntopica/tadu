import hashlib
from pathlib import Path

from tadu.workspace_port import workspace_port


def test_port_is_stable_and_in_range(tmp_path: Path) -> None:
    digest = hashlib.sha256(str(tmp_path.resolve()).encode()).hexdigest()
    assert workspace_port(tmp_path) == 40000 + int(digest, 16) % 10000
    assert workspace_port(str(tmp_path)) == workspace_port(tmp_path)
    assert 40000 <= workspace_port(tmp_path / "other") < 50000
