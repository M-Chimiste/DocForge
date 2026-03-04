# Development

This guide covers setting up a development environment and common development workflows for contributing to DocForge.

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 22+ | Frontend runtime |
| npm | 10+ | Frontend package manager |
| conda/miniforge | Latest | Python environment management |
| Git | Latest | Version control |

## Environment Setup

### Backend

```bash
# Clone the repository
git clone https://github.com/m-chimiste/docforge.git
cd docforge

# Create conda environment
conda create -n docforge python=3.12
conda activate docforge

# Install backend with dev dependencies
cd backend
pip install -e ".[dev]"
```

### Frontend

```bash
cd frontend
npm install
```

## Running Development Servers

Start the backend and frontend in separate terminals:

```bash
# Terminal 1: Backend API server (hot reload on :8000)
conda activate docforge
cd backend
uvicorn main:app --reload

# Terminal 2: Frontend dev server (hot reload on :5173)
cd frontend
npm run dev
```

The frontend dev server proxies `/api` requests to `localhost:8000` automatically.

## Testing

### Backend Tests

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

### Test Fixtures

Test fixtures (`.docx` files and data files) are created programmatically in `tests/fixtures/create_fixtures.py`. This ensures tests are deterministic and do not depend on external files.

To regenerate fixtures:

```bash
conda run -n docforge python tests/fixtures/create_fixtures.py
```

### Frontend Lint

```bash
cd frontend
npm run lint
```

### Frontend Build

```bash
cd frontend
npm run build
```

## Linting and Formatting

### Backend

DocForge uses [ruff](https://docs.astral.sh/ruff/) for Python linting and formatting:

```bash
# Check for lint errors
conda run -n docforge ruff check .

# Auto-format code
conda run -n docforge ruff format .
```

Ruff is configured in `pyproject.toml`:

- Target: Python 3.10+
- Line length: 100
- Selected rules: E, F, W, I, N, UP, B
- API files allow FastAPI's `File()`, `Depends()` in defaults (`B008` suppressed)

### Frontend

ESLint is used for frontend linting:

```bash
cd frontend
npm run lint
```

## Type Checking

### Backend

```bash
conda run -n docforge mypy .
```

MyPy is configured in `pyproject.toml` with `warn_return_any` and `warn_unused_configs` enabled.

### Frontend

TypeScript type checking is part of the build process:

```bash
cd frontend
npm run build
```

## CLI Usage

DocForge provides a CLI for template analysis and document generation:

```bash
# Analyze a template
conda run -n docforge python -m cli analyze --template path/to/template.docx

# Generate a document
conda run -n docforge python -m cli generate \
  --template path/to/template.docx \
  --data path/to/data.xlsx \
  --mapping '{"marker_0": {"dataSource": "data.xlsx", "field": "name"}}' \
  --output output.docx
```

## Docker Development

Build and run the full stack with Docker:

```bash
docker compose up
```

For development with rebuilds:

```bash
docker compose up --build
```

## Database

DocForge uses SQLite for development. The database file is created automatically on first run. To reset the database, delete the SQLite file and restart the server.

The database schema is managed by SQLAlchemy models in `db/models.py`. Tables are created automatically at startup.

## Adding a New Renderer

1. Create a new file in `backend/renderers/` (e.g., `my_renderer.py`).
2. Implement `BaseRenderer` with `can_handle()` and `render()`.
3. Register it in the engine's renderer setup.
4. Add tests in `tests/`.

## Adding a New Extractor

1. Create a new file in `backend/extractors/` (e.g., `my_extractor.py`).
2. Implement `BaseExtractor` with `can_handle()` and `extract()`.
3. Register it in the engine's extractor setup.
4. Add tests in `tests/`.

## Adding a New API Endpoint

1. Create or modify a route file in `backend/api/`.
2. Define request/response schemas in `api/schemas.py`.
3. Register the router in `api/router.py`.
4. Add tests for the endpoint.

## Project Organization

- Feature branches from `main`.
- Every renderer, extractor, and transform gets its own test file with fixture-based tests.
- Integration tests use curated template + data file combinations.
- LLM tests use mocked responses -- never hit real APIs in CI.
