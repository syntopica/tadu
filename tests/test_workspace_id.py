from pathlib import Path

from tadu.workspace_digest import workspace_digest
from tadu.workspace_id import workspace_id


def test_twelve_hex_digits(tmp_path: Path) -> None:
    assert workspace_id(tmp_path) == workspace_digest(tmp_path)[:12]
    assert len(workspace_id(tmp_path)) == 12
