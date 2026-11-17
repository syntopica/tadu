"""The check for each key of a task file."""

from __future__ import annotations

from tadu.actor_pattern import ACTOR_PATTERN
from tadu.check_task_actor import check_task_actor
from tadu.check_task_date import check_task_date
from tadu.check_task_estimate import check_task_estimate
from tadu.check_task_id import check_task_id
from tadu.check_task_lines import check_task_lines
from tadu.check_task_slug import check_task_slug
from tadu.check_task_text import check_task_text
from tadu.check_task_title import check_task_title
from tadu.choice_check import choice_check
from tadu.label_pattern import LABEL_PATTERN
from tadu.list_check import list_check
from tadu.queues import QUEUES
from tadu.task_format_version import TASK_FORMAT_VERSION
from tadu.task_id_pattern import TASK_ID_PATTERN
from tadu.task_priorities import TASK_PRIORITIES
from tadu.task_states import TASK_STATES
from tadu.uri_pattern import URI_PATTERN

TASK_VALUE_CHECKS = {
    "tadu": choice_check((TASK_FORMAT_VERSION,)),
    "id": check_task_id,
    "title": check_task_title,
    "state": choice_check(TASK_STATES),
    "category": check_task_slug,
    "type": check_task_slug,
    "priority": choice_check(TASK_PRIORITIES),
    "labels": list_check(lambda item: bool(LABEL_PATTERN.match(item)), "slugs"),
    "milestone": check_task_slug,
    "created": check_task_date,
    "created_by": check_task_actor,
    "started": check_task_date,
    "due": check_task_date,
    "defer_until": check_task_date,
    "queue": choice_check(QUEUES),
    "assignees": list_check(
        lambda item: bool(ACTOR_PATTERN.match(item)), "person ids or agent:<name>"
    ),
    "estimate": check_task_estimate,
    "parent": check_task_id,
    "blocked_by": list_check(lambda item: bool(TASK_ID_PATTERN.match(item)), "task ids"),
    "related": list_check(lambda item: bool(TASK_ID_PATTERN.match(item)), "task ids"),
    "discovered_from": check_task_id,
    "blocker": check_task_text,
    "unblock": check_task_text,
    "notes": check_task_lines,
    "done_when": check_task_lines,
    "links": list_check(lambda item: bool(URI_PATTERN.match(item)), "URIs"),
    "closed": check_task_date,
    "result": check_task_text,
    "evidence": check_task_lines,
    "resolution": check_task_text,
    "superseded_by": check_task_id,
    "duplicate_of": check_task_id,
    "files": list_check(lambda item: bool(item.strip()), "paths"),
}
