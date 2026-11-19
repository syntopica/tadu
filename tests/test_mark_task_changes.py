from tadu.mark_task_changes import mark_task_changes


def test_states_notes_and_fields_become_task_changes() -> None:
    assert mark_task_changes("blocked", "Waiting on the vendor.", ()) == [
        "state=blocked",
        "blocker=Waiting on the vendor.",
    ]
    assert mark_task_changes("open", None, (("Priority", "high"),)) == [
        "state=pending",
        "blocker=",
        "priority=high",
    ]
    fields = (("Assignees", "ana, bo"), ("Not before", "2026-12-01"), ("Estimate", "30"))
    assert mark_task_changes(None, "Seen twice.", fields) == [
        "notes+=Seen twice.",
        "assignees=ana, bo",
        "defer_until=2026-12-01",
        "estimate=30",
    ]
