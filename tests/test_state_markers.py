from tadu.state_markers import STATE_MARKERS


def test_state_markers_are_the_five_states() -> None:
    assert STATE_MARKERS == ("`[ ]`", "`[~]`", "`[!]`", "`[x]`", "`[-]`")
