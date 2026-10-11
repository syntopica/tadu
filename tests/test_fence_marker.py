from tadu.fence_marker import fence_marker


def test_returns_the_fence_run() -> None:
    assert fence_marker("```python") == "```"
    assert fence_marker("  ~~~~~") == "~~~~~"


def test_none_for_ordinary_lines() -> None:
    assert fence_marker("plain") is None
