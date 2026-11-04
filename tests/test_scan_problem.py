from tadu.scan_problem import ScanProblem


def test_fields() -> None:
    problem = ScanProblem("shop", "bad")
    assert (problem.repository, problem.message) == ("shop", "bad")
