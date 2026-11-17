from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from attention_repo import attention_repo

from tadu.cli import main


def test_priority_and_overdue_by_section(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = attention_repo(tmp_path)
    assert main(["urgent", str(repo)]) == 0
    assert capsys.readouterr().out == (
        "Do: tasks that can be done now\n"
        "shop:TODO.md:1 [backlog] urgent Fix payments.\n"
        "\n"
        "Chase: waiting on others, follow-up due\n"
        "shop:TODO.md:11 [backlog/waiting] - Carrier key.\n"
    )


def test_days_widens_the_window(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    today = datetime.now(UTC).astimezone().date()
    soon = (today + timedelta(days=3)).isoformat()
    repo = attention_repo(tmp_path, f"- [ ] Renew the domain.\n\n  Due: {soon}\n")
    assert main(["urgent", str(repo)]) == 0
    tomorrow = (today + timedelta(days=1)).isoformat()
    assert capsys.readouterr() == (
        "",
        f"tadu urgent: nothing is urgent, high priority or due by {tomorrow}\n",
    )
    assert main(["urgent", str(repo), "--days", "3", "--json"]) == 0
    assert '"section": "do"' in capsys.readouterr().out
