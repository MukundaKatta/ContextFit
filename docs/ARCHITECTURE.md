# Architecture

## Overview

ContextFit is a context window packing optimizer that helps developers maximize information density when constructing prompts for Large Language Models (LLMs).

## Module Structure

```
src/contextfit/
  __init__.py      Public API exports
  config.py        Configuration models (Pydantic)
  core.py          ContextFit engine and packing strategies
  utils.py         Token estimation and text utilities
```

## Core Concepts

### Chunk

A `Chunk` is the atomic unit of content. Each chunk has:

- **text** — the content string
- **priority** — an integer weight (higher = more important)
- **metadata** — arbitrary key-value data for the caller
- **token_count** — estimated token count (computed on creation)

### Packing Strategies

| Strategy | Algorithm |
|---|---|
| `greedy` | Iterates chunks in insertion order, adding each if it fits within the remaining token budget. Simple and predictable. |
| `priority-first` | Sorts chunks descending by priority, then applies greedy packing. Ensures the most important content is included first. |
| `balanced` | Ranks chunks by `priority / token_count` (density score), then applies greedy packing. Maximizes information value per token spent. |

### PackResult

The output of `pack()` is a `PackResult` containing:

- **chunks** — the list of packed `Chunk` objects
- **total_tokens** — sum of token counts for packed chunks
- **utilization** — ratio of tokens used vs. budget
- **strategy** — which strategy was applied

## Data Flow

```
User adds chunks
       |
       v
  Chunk Store (list)
       |
   pack() called
       |
       v
  Strategy sorts/filters chunks
       |
       v
  Greedy bin-packing loop
       |
       v
  PackResult returned
```

## Design Decisions

- **No external tokenizer dependency** — token counts are estimated using a configurable words-to-tokens ratio (default 1.33). This keeps the library lightweight. Users who need exact counts can subclass or provide a custom estimator.
- **Pydantic models** — all configuration and data structures use Pydantic v2 for validation, serialization, and clear schemas.
- **Immutable packing** — `pack()` does not mutate the internal chunk list; it returns a new result each time, allowing the caller to experiment with different strategies and budgets.
