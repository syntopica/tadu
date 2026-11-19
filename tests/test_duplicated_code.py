import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def test_jscpd_finds_no_copied_code_anywhere() -> None:
    jscpd = ROOT / "node_modules" / ".bin" / "jscpd"
    if shutil.which("node") is None or not jscpd.is_file():
        pytest.skip("needs Node.js and `npm ci` (jscpd)")
    done = subprocess.run(  # noqa: S603
        [str(jscpd), "--no-colors"], cwd=ROOT, capture_output=True, check=False, text=True
    )
    assert done.returncode == 0, done.stdout
    assert "Found 0 clones." in done.stdout
