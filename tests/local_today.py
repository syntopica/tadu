from datetime import UTC, date, datetime


def local_today() -> date:
    """Today on this machine, as tadu's commands count it."""
    return datetime.now(UTC).astimezone().date()
