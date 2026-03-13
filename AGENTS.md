# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

DocForge is an open-source, template-driven document generation engine with a web-based interface. Users author .docx templates using red-formatted text (`#FF0000`) as instructions — the system parses templates, auto-resolves data mappings, generates documents (with optional LLM support), and provides a built-in editor for proofing and export.

## Tech Stack

- **Frontend:** React 19 + TypeScript, MUI (Material UI), Vite
- **Backend:** Python 3.12, FastAPI, uvicorn
- **Document Engine:** python-docx + lxml (for advanced XML/red text detection at run level)
- **Data Processing:** pandas, openpyxl
- **LLM Integration:** LLMFactory (M-Chimiste/LLMFactory — provider-agnostic; Phase 3)
- **Storage:** SQLite + SQLAlchemy 2.0
- **Deployment:** Docker / Docker Compose
- **Testing:** pytest (backend), eslint (frontend)
- **Linting:** ruff (backend), eslint (frontend)

## Environment Setup

```bash
# Python environment (conda/miniforge)
conda activate docforge               # Python 3.12 conda environment
cd backend && pip install -e ".[dev]"  # Install backend in editable mode

# Frontend
cd frontend && npm install
```

## Development Commands

```bash
# Backend tests (always use conda env)
conda run -n docforge pytest                                  # all tests
conda run -n docforge pytest tests/test_template_parser.py    # single file
conda run -n docforge pytest tests/test_engine.py -k "test_placeholder"  # single test
conda run -n docforge pytest --cov -v                         # with coverage

# Backend lint
conda run -n docforge ruff check .
conda run -n docforge ruff format .

# Frontend
cd frontend && npm run lint
cd frontend && npm run build

# CLI
conda run -n docforge python -m cli analyze --template <path>
conda run -n docforge python -m cli generate --template <path> --data <path> --mapping <json> --output <path>

# Backend dev server (hot reload on :8000)
conda run -n docforge uvicorn main:app --reload

# Frontend dev (hot reload on :5173, proxies /api to :8000)
cd frontend && npm run dev

# Docker (full stack)
docker compose up
```

## Architecture

**Layered monolith** — single deployable unit with clean internal boundaries.

```
Presentation (React) → API (FastAPI) → Service (Engine, Parser, Renderer) → Infrastructure (SQLite, FS)
```

**Core pipeline:** Template → Parse → Ingest → Render → Output (.docx)

### Directory Structure

```
backend/
  api/          # FastAPI routes (projects, templates, data_sources, generation)
  core/         # template_parser, engine, data_loader, models (domain types)
  renderers/    # base + placeholder_renderer, table_renderer
  extractors/   # base + excel, csv, json extractors
  db/           # SQLAlchemy models + database init
  utils/        # red_text detection, docx_helpers, formatting
  tests/        # pytest tests + fixtures/ (programmatic .docx + data files)

frontend/src/
  api/          # Typed Axios client
  types/        # TS interfaces matching API schemas
  components/   # Layout, TemplateUpload, TemplateAnalysisView, DataSourceUpload, MappingPanel, GenerateButton
  pages/        # ProjectsPage, WorkspacePage
```

### Key Patterns

- **Renderer Strategy + Registry:** Pluggable renderers implement `BaseRenderer` with `can_handle()` and `render()`. Registered in priority order via `RendererRegistry`.
- **Extractor Strategy:** Same registry pattern — `BaseExtractor` with `can_handle()` and `extract()`.
- **Red text classification rule chain:** sample data (in table rows) → variable placeholder (1-3 words, noun/label) → LLM prompt (default).
- **Fail-forward error handling:** Individual render failures don't abort generation — they're recorded in results, and the section keeps its original red text.
- **LLM context is section-scoped by default** (Phase 3).

## Conventions

| Area | Convention |
|------|-----------|
| Backend modules/functions | `snake_case` |
| Backend classes | `PascalCase` |
| Frontend components | `PascalCase` |
| Frontend functions/props | `camelCase` |
| Database tables/columns | `snake_case` |
| API JSON keys | `camelCase` (Pydantic aliases) |
| API URLs | `/api/v1/projects`, `/api/v1/templates/analyze`, etc. |
| API errors | `{ "error": "code", "message": "...", "details": {} }` |

## Critical Design Decisions

- Red text detected by exact RGB `#FF0000` match at the Word run level — no tolerance range
- All LLM features are optional — system is fully functional with zero API keys
- Test fixtures (.docx) created programmatically via `tests/fixtures/create_fixtures.py`
- `MarkerType.LLM_PROMPT` exists from day one; `LLMRenderer` will be added in Phase 3 via the registry

## Planning Documents

Detailed specs in `project_docs/`:
- `DocForge_ProjectBrief.md` — project overview and design decisions
- `DocForge_PRD.md` — full product requirements
- `DocForge_TechContext.md` — technology choices, constraints
- `DocForge_SystemPatterns.md` — architectural patterns and code conventions
- `DocForge_ImplementationPlan.md` — 5-phase roadmap
