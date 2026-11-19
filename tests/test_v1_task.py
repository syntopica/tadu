from tadu.v1_task import v1_task


def test_an_estimate_is_kept_only_as_whole_minutes() -> None:
    def estimate(text: str) -> object:
        block = ("- [ ] Ship it", "", f"  Estimate: {text}")
        return v1_task(block, None, "TODO.md:1")[0].get("estimate")

    assert estimate("90") == 90
    assert estimate("\u00b2") is None
    assert estimate("1h") is None
