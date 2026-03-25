"""Core packing engine for ContextFit."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from contextfit.config import ContextFitConfig
from contextfit.utils import estimate_tokens, simple_relevance_score, truncate_text

Strategy = Literal["greedy", "priority-first", "balanced"]


class Chunk(BaseModel):
    """A single unit of content to be packed into the context window."""

    text: str
    priority: int = Field(default=5, ge=0, le=10)
    metadata: dict[str, Any] = Field(default_factory=dict)
    token_count: int = Field(default=0, ge=0)


class PackResult(BaseModel):
    """Result returned by :meth:`ContextFit.pack`."""

    chunks: list[Chunk] = Field(default_factory=list)
    total_tokens: int = 0
    utilization: float = 0.0
    strategy: Strategy = "greedy"

    @property
    def text(self) -> str:
        """Joined text of all packed chunks (double-newline separated)."""
        return "\n\n".join(c.text for c in self.chunks)


class ContextFit:
    """Context window packing optimizer.

    Add content chunks, then call :meth:`pack` with a token budget and a
    packing strategy to get an optimally packed result.

    Example::

        cf = ContextFit()
        cf.add_chunk("Hello world", priority=8)
        cf.add_chunk("More content", priority=3)
        result = cf.pack(max_tokens=50, strategy="priority-first")
    """

    def __init__(self, config: ContextFitConfig | None = None) -> None:
        self._config = config or ContextFitConfig()
        self._chunks: list[Chunk] = []
        self._last_result: PackResult | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_chunk(
        self,
        text: str,
        priority: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Chunk:
        """Add a content chunk to the internal store.

        Parameters
        ----------
        text:
            The content string.
        priority:
            Importance weight (0-10, higher is more important).
            Defaults to ``config.default_priority``.
        metadata:
            Arbitrary key-value data attached to the chunk.

        Returns
        -------
        Chunk
            The newly created chunk (with ``token_count`` populated).
        """
        if priority is None:
            priority = self._config.default_priority
        token_count = self.estimate_tokens(text)
        chunk = Chunk(
            text=text,
            priority=priority,
            metadata=metadata or {},
            token_count=token_count,
        )
        self._chunks.append(chunk)
        return chunk

    def pack(
        self,
        max_tokens: int,
        strategy: Strategy = "greedy",
    ) -> PackResult:
        """Pack stored chunks into a context window of *max_tokens*.

        Parameters
        ----------
        max_tokens:
            The token budget for the context window.
        strategy:
            One of ``"greedy"``, ``"priority-first"``, or ``"balanced"``.

        Returns
        -------
        PackResult
            Contains the selected chunks, total token usage, and utilization.
        """
        if max_tokens <= 0:
            result = PackResult(strategy=strategy)
            self._last_result = result
            return result

        ordered = self._apply_strategy(strategy)
        selected: list[Chunk] = []
        used = 0

        for chunk in ordered:
            if used + chunk.token_count <= max_tokens:
                selected.append(chunk)
                used += chunk.token_count

        utilization = used / max_tokens if max_tokens > 0 else 0.0

        result = PackResult(
            chunks=selected,
            total_tokens=used,
            utilization=utilization,
            strategy=strategy,
        )
        self._last_result = result
        return result

    def estimate_tokens(self, text: str) -> int:
        """Estimate the token count for *text* using the configured ratio."""
        return estimate_tokens(text, self._config.tokens_per_word)

    def get_utilization(self) -> float:
        """Return utilization ratio from the most recent :meth:`pack` call.

        Returns 0.0 if ``pack`` has not been called yet.
        """
        if self._last_result is None:
            return 0.0
        return self._last_result.utilization

    def reorder_by_relevance(self, query: str) -> None:
        """Re-sort the internal chunk list by relevance to *query*.

        Uses a simple term-overlap heuristic.  Ties are broken by the
        original priority (descending).
        """
        self._chunks.sort(
            key=lambda c: (simple_relevance_score(c.text, query), c.priority),
            reverse=True,
        )

    def trim_to_fit(self, text: str, max_tokens: int) -> str:
        """Truncate *text* at word boundaries to fit within *max_tokens*."""
        return truncate_text(text, max_tokens, self._config.tokens_per_word)

    def get_stats(self) -> dict[str, Any]:
        """Return summary statistics about the current chunk store."""
        total_tokens = sum(c.token_count for c in self._chunks)
        priorities = [c.priority for c in self._chunks]
        return {
            "num_chunks": len(self._chunks),
            "total_tokens": total_tokens,
            "avg_priority": sum(priorities) / len(priorities) if priorities else 0.0,
            "min_priority": min(priorities) if priorities else 0,
            "max_priority": max(priorities) if priorities else 0,
        }

    def clear(self) -> None:
        """Remove all stored chunks and reset packing state."""
        self._chunks.clear()
        self._last_result = None

    @property
    def chunks(self) -> list[Chunk]:
        """Read-only view of the current chunk store."""
        return list(self._chunks)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_strategy(self, strategy: Strategy) -> list[Chunk]:
        """Return chunks ordered according to *strategy*."""
        if strategy == "greedy":
            return list(self._chunks)
        elif strategy == "priority-first":
            return sorted(self._chunks, key=lambda c: c.priority, reverse=True)
        elif strategy == "balanced":
            return sorted(
                self._chunks,
                key=lambda c: (c.priority / max(c.token_count, 1)),
                reverse=True,
            )
        else:
            raise ValueError(f"Unknown strategy: {strategy!r}")
