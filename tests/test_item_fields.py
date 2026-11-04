from tadu.item_fields import ItemFields


def test_defaults() -> None:
    fields = ItemFields()
    assert fields.id is None
    assert fields.priority is None
    assert fields.due is None
    assert fields.assignees == ()
    assert fields.labels == ()
    assert fields.queue == "backlog"
    assert fields.estimate is None
