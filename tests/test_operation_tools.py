from tadu.operation_tools import operation_tools

READS = ["list", "show", "changes", "ready", "next", "inbox", "urgent", "similar", "feed"]
WRITES = ["add", "close", "mark", "set", "claim"]
ADMIN = ["sync", "init", "archive", "fmt", "migrate"]


def test_each_level_offers_more() -> None:
    assert list(operation_tools("read")) == [*READS, "doctor"]
    assert list(operation_tools("write")) == [*READS, "doctor", *WRITES]
    assert list(operation_tools("admin")) == [*READS, "doctor", *WRITES, *ADMIN]


def test_an_unknown_level_offers_nothing_it_does_not_know() -> None:
    assert operation_tools("admin")["add"]["name"] == "add"
    assert "board" not in operation_tools("admin")
