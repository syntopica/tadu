"""Every tadu operation by name, in the order `tadu --help` lists them."""

from __future__ import annotations

from tadu.add_operation import ADD_OPERATION
from tadu.admin_operations import ADMIN_OPERATIONS
from tadu.attention_operations import ATTENTION_OPERATIONS
from tadu.close_operation import CLOSE_OPERATION
from tadu.history_operations import HISTORY_OPERATIONS
from tadu.list_operation import LIST_OPERATION
from tadu.local_operations import LOCAL_OPERATIONS
from tadu.lookup_operations import LOOKUP_OPERATIONS
from tadu.mark_operation import MARK_OPERATION
from tadu.task_operations import TASK_OPERATIONS

# keys: operation names are distinct literals, and test_operations lists them.
OPERATIONS = {
    operation.name: operation
    for operation in (
        LIST_OPERATION,
        *HISTORY_OPERATIONS,
        *ATTENTION_OPERATIONS,
        *LOOKUP_OPERATIONS,
        ADD_OPERATION,
        CLOSE_OPERATION,
        MARK_OPERATION,
        *TASK_OPERATIONS,
        *ADMIN_OPERATIONS,
        *LOCAL_OPERATIONS,
    )
}
