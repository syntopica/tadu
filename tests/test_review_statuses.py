from tadu.review_statuses import REVIEW_STATUSES


def test_review_statuses_are_the_four_coverage_states() -> None:
    assert {"complete", "partial", "inaccessible", "irrelevant"} == REVIEW_STATUSES
