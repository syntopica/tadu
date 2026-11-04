from tadu.field_problem import FieldProblem


def test_holds_line_and_message() -> None:
    problem = FieldProblem(3, "msg")
    assert (problem.line, problem.message) == (3, "msg")
