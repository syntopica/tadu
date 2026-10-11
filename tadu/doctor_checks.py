"""The checks the doctor command runs on each root."""

from __future__ import annotations

from tadu.check_history_index import check_history_index
from tadu.check_log_file import check_log_file
from tadu.check_rule_block import check_rule_block
from tadu.check_todo_file import check_todo_file

DOCTOR_CHECKS = (check_todo_file, check_log_file, check_history_index, check_rule_block)
