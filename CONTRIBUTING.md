# Contributing to DocForge

Thank you for your interest in contributing to DocForge! This guide will help you get started.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Running Tests](#running-tests)
- [Linting and Formatting](#linting-and-formatting)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Adding Plugins](#adding-plugins)
- [Issue Guidelines](#issue-guidelines)

## Development Environment Setup

### Backend (Python)

DocForge uses Python 3.12 with a conda environment.

```bash
# Create and activate the conda environment
conda create -n docforge python=3.12
conda activate docforge

# Install backend in editable mode with dev dependencies
cd backend
pip install -e ".[dev]"
```

### Frontend (React + TypeScript)

```bash
cd frontend
npm install
```

### Full Stack (Docker)

```bash
docker compose up
```

## Running Tests

### Backend

Always run backend tests within the conda environment:

```bash
# Run all tests
conda run -n docforge pytest

# Run a specific test file
conda run -n docforge pytest tests/test_template_parser.py

# Run a specific test
conda run -n docforge pytest tests/test_engine.py -k "test_placeholder"

# Run with coverage
conda run -n docforge pytest --cov -v
```

### Frontend

```bash
cd frontend && npm run lint
cd frontend && npm run build
```

## Linting and Formatting

### Backend

DocForge uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting:

```bash
# Check for lint issues
conda run -n docforge ruff check .

# Auto-format code
conda run -n docforge ruff format .
```

### Frontend

```bash
cd frontend && npm run lint
```

## Code Style

| Area | Convention | Example |
|------|-----------|---------|
| Python modules and functions | `snake_case` | `template_parser.py`, `def parse_template()` |
| Python classes | `PascalCase` | `class PlaceholderRenderer` |
| React components | `PascalCase` | `MappingPanel.tsx` |
| Frontend functions and props | `camelCase` | `onTemplateUpload`, `projectId` |
| Database tables and columns | `snake_case` | `data_sources`, `created_at` |
| API JSON keys | `camelCase` | `{ "projectId": "..." }` (via Pydantic aliases) |
| API URLs | lowercase with hyphens | `/api/v1/projects`, `/api/v1/templates/analyze` |

### Additional Guidelines

- Write docstrings for all public functions and classes.
- Keep functions focused and short.
- Use type hints in Python code.
- Use TypeScript types (not `any`) in frontend code.

## Pull Request Process

1. **Fork** the repository and clone your fork locally.
2. **Create a branch** from `main` with a descriptive name:
   ```bash
   git checkout -b feat/batch-generation
   git checkout -b fix/red-text-detection
   ```
3. **Make your changes** with clear, atomic commits.
4. **Run tests and linting** to ensure everything passes:
   ```bash
   conda run -n docforge pytest
   conda run -n docforge ruff check .
   cd frontend && npm run lint && npm run build
   ```
5. **Push** your branch and open a Pull Request against `main`.
6. **Fill out the PR template** completely.
7. **Address review feedback** promptly.

### Commit Message Format

Use clear, imperative-mood commit messages:

```
Add table renderer for multi-row output
Fix red text detection for nested runs
Update mapping panel to show confidence scores
```

## Adding Plugins

DocForge uses a registry pattern for renderers, extractors, and transforms. Adding a new plugin follows the same pattern for each type.

### Adding a Renderer

1. Create a new file in `backend/renderers/` (e.g., `my_renderer.py`).
2. Subclass `BaseRenderer` and implement `can_handle()` and `render()`.
3. Register it in the `RendererRegistry` with an appropriate priority.

```python
from renderers.base import BaseRenderer

class MyRenderer(BaseRenderer):
    def can_handle(self, marker) -> bool:
        # Return True if this renderer handles the given marker
        ...

    def render(self, marker, context) -> str:
        # Return the rendered content
        ...
```

### Adding an Extractor

1. Create a new file in `backend/extractors/` (e.g., `my_extractor.py`).
2. Subclass `BaseExtractor` and implement `can_handle()` and `extract()`.
3. Register it in the extractor registry.

For more details on the plugin architecture, see the [System Patterns documentation](project_docs/DocForge_SystemPatterns.md).

## Issue Guidelines

Before opening an issue:

1. **Search existing issues** to avoid duplicates.
2. **Use the issue templates** provided:
   - [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md) for bugs
   - [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md) for new features
3. **Provide context**: include version numbers, OS, and steps to reproduce.
4. **Be specific**: "the mapping panel crashes" is less helpful than "the mapping panel throws a TypeError when dragging a field with special characters."

## Questions?

If you have questions about contributing, open a [Discussion](https://github.com/M-Chimiste/DocForge/discussions) or reach out to the maintainers.

Thank you for helping make DocForge better!
