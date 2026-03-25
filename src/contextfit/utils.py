"""Utility functions for ContextFit."""

from __future__ import annotations

import math
import re


def estimate_tokens(text: str, tokens_per_word: float = 1.33) -> int:
    """Estimate the number of tokens in *text*.

    Uses a simple heuristic: split on whitespace, multiply word count by
    *tokens_per_word*, and round up.  This avoids a hard dependency on any
    specific tokenizer while giving a reasonable approximation for English
    prose.
    """
    if not text or not text.strip():
        return 0
    words = text.split()
    return max(1, math.ceil(len(words) * tokens_per_word))


def truncate_text(text: str, max_tokens: int, tokens_per_word: float = 1.33) -> str:
    """Truncate *text* so its estimated token count is at most *max_tokens*.

    Truncation is performed at word boundaries.  If the entire text already
    fits, it is returned unchanged.
    """
    if max_tokens <= 0:
        return ""
    words = text.split()
    if not words:
        return ""
    # Binary-ish approach: keep adding words until we exceed the budget
    max_words = max(1, math.floor(max_tokens / tokens_per_word))
    kept = words[:max_words]
    return " ".join(kept)


def simple_relevance_score(text: str, query: str) -> float:
    """Compute a naive relevance score between *text* and *query*.

    The score is the fraction of unique query terms (case-insensitive) that
    appear in *text*.  Returns a float in [0.0, 1.0].
    """
    if not query.strip():
        return 0.0
    query_terms = set(re.findall(r"\w+", query.lower()))
    if not query_terms:
        return 0.0
    text_lower = text.lower()
    matches = sum(1 for term in query_terms if term in text_lower)
    return matches / len(query_terms)
