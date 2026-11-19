from history_entries import ENTRIES

from tadu.change_entry import ChangeEntry

EVENTS = ["changed", "closed", "started", "changed", "created"]
CHANGES = [
    ChangeEntry(
        **entry,
        repository="shop",
        project=None,
        key=f"t-{n:08x}-0000-4000-8000-000000000000" if n % 2 else None,
        title=f"Task {n}",
        event=event,
    )
    for n, (entry, event) in enumerate(zip(ENTRIES, EVENTS, strict=True))
]
