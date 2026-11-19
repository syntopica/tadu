from datetime import date
from pathlib import Path

from sample_task import sample_id, sample_task
from task_backlog import task_backlog

from tadu.path_cards import path_cards
from tadu.reverse_relation_index import reverse_relation_index


def test_each_target_lists_who_points_at_it(tmp_path: Path) -> None:
    one = sample_id(1)
    tasks = [sample_task(1), sample_task(2, parent=one), sample_task(3, related=[one], parent=one)]
    cards, _ = path_cards((str(task_backlog(tmp_path, tasks)),), date.min)
    index = reverse_relation_index(cards)
    assert [(name, card.item.key[:10]) for name, card in index[one]] == [
        ("children", "t-00000002"),
        ("children", "t-00000003"),
        ("related (linked from)", "t-00000003"),
    ]
    assert list(index) == [one]
