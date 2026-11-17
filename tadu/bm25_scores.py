"""Rank documents against a query with BM25."""

from __future__ import annotations

import math
from collections import Counter


def bm25_scores(
    query: tuple[str, ...], documents: tuple[tuple[str, ...], ...]
) -> tuple[float, ...]:
    """One BM25 score per document (k1 = 1.2, b = 0.75); 0 when it shares no query word."""
    wanted = set(query)
    count = len(documents)
    average = sum(len(doc) for doc in documents) / count if count else 0.0
    frequency = Counter(word for doc in documents for word in set(doc) if word in wanted)
    scores: list[float] = []
    for doc in documents:
        terms = Counter(word for word in doc if word in wanted)
        score = 0.0
        for word, hits in terms.items():
            idf = math.log(1 + (count - frequency[word] + 0.5) / (frequency[word] + 0.5))
            score += idf * hits * 2.2 / (hits + 1.2 * (0.25 + 0.75 * len(doc) / average))
        scores.append(score)
    return tuple(scores)
