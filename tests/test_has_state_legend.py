from tadu.has_state_legend import has_state_legend


def test_legend_needs_all_five_markers() -> None:
    assert has_state_legend("`[ ]` `[~]` `[!]` `[x]` `[-]`")
    assert not has_state_legend("`[ ]` `[x]`")
