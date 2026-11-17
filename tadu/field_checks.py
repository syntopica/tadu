"""Validator for each field name."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tadu.check_assignees_value import check_assignees_value
from tadu.check_check_on_value import check_check_on_value
from tadu.check_due_value import check_due_value
from tadu.check_estimate_value import check_estimate_value
from tadu.check_id_value import check_id_value
from tadu.check_kind_value import check_kind_value
from tadu.check_labels_value import check_labels_value
from tadu.check_not_before_value import check_not_before_value
from tadu.check_priority_value import check_priority_value
from tadu.check_queue_value import check_queue_value

if TYPE_CHECKING:
    from collections.abc import Callable

FIELD_CHECKS: dict[str, Callable[[str], str | None]] = {
    "ID": check_id_value,
    "Priority": check_priority_value,
    "Assignees": check_assignees_value,
    "Due": check_due_value,
    "Labels": check_labels_value,
    "Queue": check_queue_value,
    "Kind": check_kind_value,
    "Check on": check_check_on_value,
    "Not before": check_not_before_value,
    "Estimate": check_estimate_value,
}
