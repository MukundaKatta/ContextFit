"""Tests for the ContextFit core engine."""

from contextfit import ContextFit, ContextFitConfig


class TestAddChunkAndEstimate:
    """Adding chunks and estimating tokens."""

    def test_add_chunk_stores_text_and_priority(self) -> None:
        cf = ContextFit()
        chunk = cf.add_chunk("Hello world", priority=8)
        assert chunk.text == "Hello world"
        assert chunk.priority == 8
        assert chunk.token_count > 0

    def test_default_priority_from_config(self) -> None:
        config = ContextFitConfig(default_priority=7)
        cf = ContextFit(config=config)
        chunk = cf.add_chunk("Some text")
        assert chunk.priority == 7

    def test_estimate_tokens_empty_string(self) -> None:
        cf = ContextFit()
        assert cf.estimate_tokens("") == 0
        assert cf.estimate_tokens("   ") == 0


class TestPackStrategies:
    """Packing with different strategies."""

    def _build_cf(self) -> ContextFit:
        cf = ContextFit()
        cf.add_chunk("short", priority=2)               # few tokens
        cf.add_chunk("a slightly longer sentence here", priority=9)  # more tokens
        cf.add_chunk("medium length text", priority=5)   # medium tokens
        return cf

    def test_greedy_respects_token_limit(self) -> None:
        cf = self._build_cf()
        result = cf.pack(max_tokens=5, strategy="greedy")
        assert result.total_tokens <= 5
        assert result.utilization <= 1.0

    def test_priority_first_selects_high_priority(self) -> None:
        cf = self._build_cf()
        result = cf.pack(max_tokens=1000, strategy="priority-first")
        # All chunks fit; first packed chunk should be highest priority
        assert result.chunks[0].priority == 9

    def test_balanced_packs_efficiently(self) -> None:
        cf = self._build_cf()
        result = cf.pack(max_tokens=1000, strategy="balanced")
        assert len(result.chunks) == 3
        assert result.utilization > 0

    def test_pack_zero_budget(self) -> None:
        cf = self._build_cf()
        result = cf.pack(max_tokens=0, strategy="greedy")
        assert len(result.chunks) == 0
        assert result.total_tokens == 0


class TestUtilityMethods:
    """Utility methods: trim, reorder, stats."""

    def test_trim_to_fit(self) -> None:
        cf = ContextFit()
        long_text = " ".join(["word"] * 100)
        trimmed = cf.trim_to_fit(long_text, max_tokens=5)
        assert cf.estimate_tokens(trimmed) <= 5

    def test_reorder_by_relevance(self) -> None:
        cf = ContextFit()
        cf.add_chunk("Python is great for scripting", priority=3)
        cf.add_chunk("Java is enterprise-grade", priority=7)
        cf.add_chunk("Python programming language", priority=5)
        cf.reorder_by_relevance("Python programming")
        # The Python-related chunks should come first
        assert "Python" in cf.chunks[0].text

    def test_get_stats(self) -> None:
        cf = ContextFit()
        cf.add_chunk("one", priority=2)
        cf.add_chunk("two", priority=8)
        stats = cf.get_stats()
        assert stats["num_chunks"] == 2
        assert stats["min_priority"] == 2
        assert stats["max_priority"] == 8
        assert stats["avg_priority"] == 5.0

    def test_get_utilization_before_pack(self) -> None:
        cf = ContextFit()
        assert cf.get_utilization() == 0.0
