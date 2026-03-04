# Architecture

This document describes DocForge's internal architecture for contributors and developers looking to understand, modify, or extend the codebase.

## Layered Monolith

DocForge uses a layered monolith architecture -- a single deployable unit with well-defined internal boundaries between layers. This is intentional: the project is too small for microservices, but needs clean separation so components can be extracted and reused independently.

```
+---------------------------------------------+
|              Presentation Layer              |
|         React Frontend (TypeScript)          |
+---------------------------------------------+
|                API Layer                     |
|       FastAPI REST Endpoints (Python)        |
+---------------------------------------------+
|              Service Layer                   |
|     Engine, Parser, Mapper, Renderer         |
+---------------------------------------------+
|            Infrastructure Layer              |
|   SQLite, File System, LLM Clients          |
+---------------------------------------------+
```

### Layer Rules

- Layers only call **downward** -- never up, never sideways across the same layer.
- The **API layer** is thin -- it validates input, delegates to the service layer, and formats output.
- The **service layer** contains all business logic and is testable without HTTP or a database.
- The **infrastructure layer** is swappable -- LLM providers, storage backends, and file formats can change without touching business logic.

## Core Pipeline

Document generation follows a pipeline pattern where the template flows through processing stages:

```
Template (.docx)
     |
     v
  Parse       --> Extract sections, tables, red text markers
     |
     v
  Resolve     --> Auto-map data sources, classify markers, scope LLM context
     |
     v
  Ingest      --> Load and normalize all data sources
     |
     v
  Render      --> Execute renderers in sequence
     |
     v
  Validate    --> Check completeness, flag low-confidence items
     |
     v
Output (.docx) + Report (.json)
```

Each stage has a single responsibility, is independently testable, and the order is deterministic. New processing steps can be inserted without restructuring the pipeline.

## Directory Structure

### Backend

```
backend/
  api/              # FastAPI routes
    projects.py     # Project CRUD
    templates.py    # Template upload and analysis
    data_sources.py # Data source upload and listing
    generation.py   # Document generation (sync)
    generation_stream.py  # Generation with SSE streaming
    editor.py       # Editor document, save, export
    llm_config.py   # LLM configuration endpoints
    auto_resolution.py    # Auto-resolve mappings
    validation.py   # Mapping validation
    data_preview.py # Data source preview
    plugins.py      # Plugin listing
    schemas.py      # Pydantic request/response models
    errors.py       # Error handling utilities
    router.py       # Route aggregation
  core/             # Business logic
    engine.py       # GenerationEngine (orchestrates the pipeline)
    template_parser.py    # .docx parsing, red text detection
    data_loader.py  # DataStore, load_data_sources()
    models.py       # Domain types (TemplateMarker, MappingEntry, etc.)
    llm_client.py   # LLM integration via LiteLLM
    llm_context.py  # ContextAssembler for section-scoped LLM context
    auto_resolver.py      # Fuzzy matching for auto-resolution
    validators.py   # Mapping validation logic
    plugin_loader.py      # Entry point discovery
    error_catalog.py      # Error codes and messages
  renderers/        # Renderer implementations
    base.py         # BaseRenderer, RendererRegistry
    placeholder_renderer.py
    table_renderer.py
    text_renderer.py
    llm_renderer.py
    conditional_renderer.py
  extractors/       # Data extractors
    base.py         # BaseExtractor, ExtractorRegistry
    excel.py, csv_extractor.py, json_extractor.py, etc.
  transforms/       # Data transforms
    base.py         # BaseTransform, TransformRegistry, TransformPipeline
    rename.py, filter.py, sort.py, etc.
  db/               # Database layer
    models.py       # SQLAlchemy models (Project, GenerationRun)
    database.py     # Database initialization
  utils/            # Shared utilities
    formatting.py   # Red text detection, docx helpers
  tests/            # Test suite
    fixtures/       # Programmatic .docx and data files
```

### Frontend

```
frontend/src/
  api/          # Typed Axios client
  types/        # TypeScript interfaces matching API schemas
  components/   # Reusable UI components
  pages/        # Page-level components (ProjectsPage, WorkspacePage)
```

## Key Design Patterns

### Strategy + Registry (Renderers, Extractors, Transforms)

All three plugin types use the same pattern:

1. An abstract base class defines the interface (`can_handle()` + action method).
2. A registry holds all implementations and iterates them in order.
3. The first implementation whose `can_handle()` returns `True` is used.
4. Third-party plugins are loaded via entry points and appended to the registry.

### Rule Chain (Red Text Classification)

Red text markers are classified using a priority-ordered rule chain:

1. Inside a table data row -> `SAMPLE_DATA`
2. 1-3 words, noun/label -> `VARIABLE_PLACEHOLDER`
3. Default -> `LLM_PROMPT`

### Fuzzy Match with Confidence Scoring (Auto-Resolution)

Data source mapping uses multiple matching strategies applied in order, each producing a confidence score. Thresholds determine whether matches are auto-accepted, flagged, or left unresolved.

### Section-Scoped LLM Context

LLM prompts receive context from their containing section by default. Broadening signals in the prompt text (e.g., "all sections", "entire document") trigger wider context assembly.

### Fail-Forward Error Handling

Individual rendering failures do not abort the pipeline. Errors are recorded in the generation report, and the affected section keeps its original content. This applies to both rendering and plugin loading.

### Server-Authoritative State

The backend is the single source of truth. The frontend uses optimistic UI updates but always reconciles with the server. Generation progress is streamed via SSE.

### Append-Only History

Each generation run creates a new database record with its own mapping snapshot, output, and report. This enables comparing outputs across runs and auditing what produced a specific document.

## Data Flow

### Template Upload

```
Frontend -> POST /api/v1/templates/analyze
         -> Engine.analyze() -> TemplateParser -> TemplateAnalysis
         <- JSON response with sections, markers, tables
```

### Document Generation

```
Frontend -> POST /api/v1/projects/{id}/generate
         -> Load project from DB
         -> Load data sources from filesystem
         -> Engine.generate()
            -> Parse template
            -> Load data into DataStore
            -> For each marker:
               -> Registry.get_renderer(marker)
               -> renderer.render(marker, data, doc, mapping)
            -> Validate results
         -> Save GenerationRun to DB
         <- JSON response with runId, downloadUrl, report
```

### Editor Flow

```
Frontend -> GET /api/v1/generations/{id}/document
         -> Convert .docx to editor JSON (or return cached state)
         <- Editor state JSON

Frontend -> PUT /api/v1/generations/{id}/document
         -> Save editor state to DB

Frontend -> POST /api/v1/generations/{id}/export
         -> Convert editor state back to .docx
         <- File download
```
