# Contributing to ContextFit

Thank you for your interest in contributing to ContextFit!

## Getting Started

1. Fork the repository.
2. Clone your fork locally.
3. Install development dependencies:

```bash
make dev
```

## Development Workflow

### Running Tests

```bash
make test
```

### Linting and Formatting

```bash
make lint
make format
```

### Type Checking

```bash
make typecheck
```

### Full CI Check

```bash
make ci
```

## Pull Requests

- Create a feature branch from `main`.
- Write tests for any new functionality.
- Ensure all checks pass (`make ci`).
- Keep commits focused and descriptive.
- Open a pull request with a clear description of the change.

## Code Style

- We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting.
- Type annotations are required for all public APIs.
- Follow existing patterns in the codebase.

## Reporting Issues

Open an issue on GitHub with a clear description and steps to reproduce.

---

Built by [Officethree Technologies](https://officethree.com)
