from tadu.git_log_format import GIT_LOG_FORMAT, RECORD, UNIT


def test_a_record_per_commit_with_separated_fields() -> None:
    assert (RECORD, UNIT) == ("\x1e", "\x1f")
    assert GIT_LOG_FORMAT == "--format=\x1e%H\x1f%P\x1f%aI\x1f%an\x1f%s"
