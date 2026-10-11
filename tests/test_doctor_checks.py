from tadu.check_history_index import check_history_index
from tadu.check_log_file import check_log_file
from tadu.check_rule_block import check_rule_block
from tadu.check_todo_file import check_todo_file
from tadu.doctor_checks import DOCTOR_CHECKS


def test_doctor_runs_the_four_checks() -> None:
    assert (check_todo_file, check_log_file, check_history_index, check_rule_block) == DOCTOR_CHECKS
