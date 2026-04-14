# ContextFit — Context window packing optimizer — maximize LLM context utilization with greedy, priority, and balanced strategies

Context window packing optimizer — maximize LLM context utilization with greedy, priority, and balanced strategies. ContextFit gives you a focused, inspectable implementation of that idea.

## Why ContextFit

ContextFit exists to make this workflow practical. Context window packing optimizer — maximize llm context utilization with greedy, priority, and balanced strategies. It favours a small, inspectable surface over sprawling configuration.

## Features

- `Chunk` — exported from `src/contextfit/core.py`
- `PackResult` — exported from `src/contextfit/core.py`
- `ContextFit` — exported from `src/contextfit/core.py`
- Included test suite
- Dedicated documentation folder

## Tech Stack

- **Runtime:** Python
- **Tooling:** Pydantic

## How It Works

The codebase is organised into `docs/`, `src/`, `tests/`. The primary entry points are `src/contextfit/core.py`, `src/contextfit/__init__.py`. `src/contextfit/core.py` exposes `Chunk`, `PackResult`, `ContextFit` — the core types that drive the behaviour.

## Getting Started

```bash
pip install -e .
```

## Usage

```python
from contextfit.core import Chunk

instance = Chunk()
# See the source for the full API
```

## Project Structure

```
ContextFit/
├── .env.example
├── CONTRIBUTING.md
├── Makefile
├── README.md
├── docs/
├── pyproject.toml
├── src/
├── tests/
```
