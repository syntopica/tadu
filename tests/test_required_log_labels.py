from tadu.required_log_labels import REQUIRED_LOG_LABELS


def test_each_closed_state_names_its_proof_line() -> None:
    assert REQUIRED_LOG_LABELS == {"x": ("L002", "Evidence:"), "-": ("L003", "Resolution:")}
