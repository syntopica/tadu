import threading
import time
from pathlib import Path

from tadu.backlog_lock import backlog_lock


def test_second_writer_waits_for_the_first(tmp_path: Path) -> None:
    order: list[str] = []

    def second() -> None:
        with backlog_lock(tmp_path):
            order.append("second")

    with backlog_lock(tmp_path):
        thread = threading.Thread(target=second)
        thread.start()
        time.sleep(0.05)
        order.append("first")
    thread.join()
    assert order == ["first", "second"]
