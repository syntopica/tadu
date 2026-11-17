"""Find the cards most like a piece of text."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from tadu.bm25_scores import bm25_scores
from tadu.title_words import title_words

if TYPE_CHECKING:
    from tadu.card import Card


def similar_cards(cards: tuple[Card, ...], text: str, limit: int) -> tuple[tuple[float, Card], ...]:
    """The best `limit` cards by BM25 over title (twice), category and labels.

    Each comes with the share of words it has in common with the text (0 to 1), which reads
    the same across queries, unlike the BM25 score.
    """
    query = title_words(text)
    documents = tuple(
        title_words(
            f"{c.item.title} {c.item.title} {c.item.extras.category or ''} {' '.join(c.item.fields.labels)}"
        )
        for c in cards
    )
    ranked = sorted(
        ((score, index) for index, score in enumerate(bm25_scores(query, documents)) if score > 0),
        key=lambda pair: -pair[0],
    )[:limit]
    asked = set(query)
    results = []
    for _, index in ranked:
        words = set(title_words(cards[index].item.title))
        overlap = (
            len(asked & words) / math.sqrt(len(asked) * len(words)) if asked and words else 0.0
        )
        results.append((overlap, cards[index]))
    return tuple(results)
