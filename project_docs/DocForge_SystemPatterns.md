# DocForge — System Patterns

**Project:** DocForge
**Date:** March 3, 2026
**Audience:** Engineers and contributors

---

## 1. Architecture Pattern: Layered Monolith with Clean Boundaries

DocForge uses a layered monolith architecture — a single deployable unit (containerized) with well-defined internal boundaries between layers. This is intentional: the project is too small for microservices, but needs clean separation so components can be extracted and reused independently (a stated project goal).

```
┌─────────────────────────────────────────────┐
│              Presentation Layer              │
│         React Frontend (TypeScript)          │
├─────────────────────────────────────────────┤
│                API Layer                     │
│       FastAPI REST Endpoints (Python)        │
├─────────────────────────────────────────────┤
│              Service Layer                   │
│     Engine, Parser, Mapper, Renderer         │
├─────────────────────────────────────────────┤
│            Infrastructure Layer              │
│   SQLite, File System, LLM Clients          │
└─────────────────────────────────────────────┘
```

**Rules:**
- Layers only call downward — never up, never sideways across the same layer
- The API layer is thin — it validates input, delegates to the service layer, and formats output
- The service layer contains all business logic and is testable without HTTP or a database
- The infrastructure layer is swappable — LLM providers, storage backends, and file formats can change without touching business logic

## 2. Core Design Pattern: Pipeline / Chain of Responsibility

Document generation follows a pipeline pattern where the template flows through a series of processing stages. Each stage reads from and writes to the document, transforming it incrementally.

```
Template (.docx)
     │
     ▼
┌─────────────┐
│ Parse       │ → Extract sections, tables, red text markers
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Resolve     │ → Auto-map data sources, classify markers, scope LLM context
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Ingest      │ → Load and normalize all data sources
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Render      │ → Execute renderers in sequence (placeholders → tables → LLM → conditionals)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Validate    │ → Check completeness, flag low-confidence items
└──────┬──────┘
       │
       ▼
Output (.docx) + Report (.json)
```

**Why pipeline:** Each stage has a single responsibility, is independently testable, and the order is deterministic. New processing steps (e.g., image injection in a future version) can be inserted without restructuring the pipeline.

## 3. Renderer Pattern: Strategy + Registry

Renderers are pluggable components that each handle one type of content injection. They implement a common interface and are registered in a renderer registry that the engine consults during the render stage.

```python
class BaseRenderer(ABC):
    """All renderers implement this interface."""
    
    @abstractmethod
    def can_handle(self, marker: TemplateMarker) -> bool:
        """Return True if this renderer handles this marker type."""
        ...
    
    @abstractmethod
    def render(self, marker: TemplateMarker, data: DataStore, document: Document) -> RenderResult:
        """Apply the rendering transformation to the document."""
        ...

class RendererRegistry:
    """Registry of available renderers, consulted in priority order."""
    
    def __init__(self):
        self._renderers: list[BaseRenderer] = []
    
    def register(self, renderer: BaseRenderer) -> None:
        self._renderers.append(renderer)
    
    def get_renderer(self, marker: TemplateMarker) -> BaseRenderer:
        for renderer in self._renderers:
            if renderer.can_handle(marker):
                return renderer
        raise NoRendererFoundError(marker)
```

**Built-in renderers:**
- `PlaceholderRenderer` — simple value substitution for variable placeholders
- `TableRenderer` — populate skeleton tables from DataFrames, including nested tables
- `TextRenderer` — inject multi-paragraph text into sections
- `LLMRenderer` — assemble context, call LLM, inject response
- `ConditionalRenderer` — include/exclude sections based on data presence

**Extensibility:** Third-party renderers can be registered via the plugin architecture (v0.5). The registry pattern means adding a new renderer requires zero changes to the engine.

## 4. Extractor Pattern: Strategy (Same as Renderers)

Data extractors follow the same strategy pattern as renderers. Each extractor handles one input format and produces a normalized output (DataFrame for structured data, text blocks for unstructured).

```python
class BaseExtractor(ABC):
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool: ...
    
    @abstractmethod
    def extract(self, file_path: Path, config: ExtractionConfig) -> ExtractedData: ...
```

**Built-in extractors:** Excel, CSV/TSV, JSON, plain text, Word (.docx), PowerPoint (.pptx), PDF, LLM-based (delegates to configured LLM for schema-driven extraction from unstructured sources).

## 5. Classification Pattern: Rule Chain with User Override

Red text classification uses a rule chain that evaluates markers in priority order. The chain produces a classification with a confidence score. Users can override any classification in the GUI, and overrides persist in the project database.

```
Red text detected
     │
     ├─ Rule 1: Is it inside a table data row?
     │          → SAMPLE_DATA (high confidence)
     │
     ├─ Rule 2: Is it 1-3 words with noun/label structure?
     │          → VARIABLE_PLACEHOLDER (medium confidence)
     │
     └─ Rule 3: Default
                → LLM_PROMPT (high confidence)
     │
     ▼
User override? → Apply and persist
```

**Key principle:** The default is LLM_PROMPT. The system only escapes from the default if a more specific rule matches. This keeps the template author's intent as the primary signal — they wrote instructions, so the system should treat them as instructions.

## 6. Auto-Resolution Pattern: Fuzzy Match with Confidence Scoring

Data source auto-resolution uses fuzzy matching to connect template markers to uploaded data. Each match gets a confidence score that determines how it's presented to the user and whether it gets flagged post-generation.

**Matching strategies (applied in order):**

1. **Exact file reference** — LLM prompt text contains a filename that matches an uploaded file → confidence: 1.0
2. **Field name match** — variable placeholder text exactly matches a column header or JSON key → confidence: 0.9
3. **Fuzzy field name match** — placeholder text is a close match to a field name (edit distance, token overlap) → confidence: 0.5-0.8
4. **Sample data structural match** — red sample data in a table matches the column count and data types of a data source → confidence: 0.6-0.8
5. **No match** — marker left unresolved → confidence: 0.0

**Confidence thresholds:**
- ≥ 0.8: Auto-resolved, no flag. Proceeds through generation silently.
- 0.4 - 0.79: Auto-resolved, flagged post-generation in the editor for user review.
- < 0.4: Left unresolved. Highlighted in the mapping GUI for manual resolution before generation.

## 7. LLM Context Assembly Pattern: Section-Scoped with Explicit Broadening

LLM context is assembled per-prompt using a scoping strategy that defaults to the containing section and expands only when explicitly signaled by the prompt text.

```
┌─────────────────────────────────────────────────┐
│ Document                                         │
│                                                  │
│ ┌─ Section: Executive Summary ────────────────┐  │
│ │ Red text: "Provide an executive summary      │  │
│ │ covering all sections"                       │  │
│ │                                              │  │
│ │ Context scope: ALL SECTIONS (explicit)       │  │
│ └──────────────────────────────────────────────┘  │
│                                                  │
│ ┌─ Section: Methods ──────────────────────────┐  │
│ │ Red text: "Summarize the methods used"       │  │
│ │                                              │  │
│ │ Context scope: SECTION ONLY (default)        │  │
│ └──────────────────────────────────────────────┘  │
│                                                  │
│ ┌─ Section: Results ──────────────────────────┐  │
│ │ Red text: "Analyze the results from          │  │
│ │ quarterly_metrics.xlsx"                      │  │
│ │                                              │  │
│ │ Context scope: SECTION + explicit file ref   │  │
│ └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Broadening signals** detected in prompt text: "all sections," "entire document," "covering all," "overall," "executive summary," or explicit cross-section references. These are detected heuristically and presented to the user for confirmation in the mapping panel.

## 8. State Management Pattern: Server-Authoritative with Optimistic UI

The backend is the single source of truth for all state: project configuration, template analysis, mapping resolution, and generation results. The frontend uses optimistic UI updates for responsiveness but always reconciles with the server.

**State flow:**
- Template upload → backend parses and returns analysis → frontend renders tree view
- Mapping change → frontend shows change immediately → API call to persist → reconcile on response
- Generate → backend runs pipeline → streams progress events via SSE → frontend updates progress bar → final result loads in editor
- Editor save → frontend captures document state → API call to persist edits → export triggered from backend

**Why SSE for generation:** Document generation involves multiple stages with variable latency (especially LLM calls). Server-Sent Events let the backend push per-stage progress updates without the complexity of WebSockets.

## 9. Project Persistence Pattern: Append-Only History

Projects in the database follow an append-only pattern for generation history. Each generation run creates a new record with its own mapping snapshot, data source references, and output. This enables:

- Comparing outputs across runs with the same template but different data
- Auditing what data and LLM settings produced a specific document
- Rolling back to a previous generation's configuration

```
Projects (1) ──→ (N) Generation Runs ──→ (1) Output Document
                                        ──→ (1) Generation Report
                                        ──→ (1) Mapping Snapshot
```

## 10. Error Handling Pattern: Fail-Forward with Report

The generation pipeline uses a fail-forward strategy: individual rendering failures (e.g., a missing data source for one table, an LLM timeout for one section) do not abort the entire generation. Instead, the failure is recorded in the generation report, the affected section is left with its original red text (or a visible error marker), and generation continues.

**Error categories:**
- **Fatal:** Template parse failure, database corruption → abort with clear error message
- **Recoverable:** Missing data source, LLM timeout, schema mismatch → skip the affected marker, record in report, continue
- **Warning:** Low-confidence mapping, unused data source, empty optional section → record in report, highlight in editor

This ensures users always get output they can work with, even if some sections need manual attention.

## 11. Key Conventions

### API Design
- RESTful endpoints with consistent URL structure: `/api/v1/projects`, `/api/v1/projects/{id}/generate`
- Pydantic models for all request/response schemas
- Consistent error response format: `{ "error": "code", "message": "human-readable", "details": {} }`

### File Organization
- Frontend: feature-based component organization (`components/`, `pages/`, `api/`)
- Backend: domain-based module organization (`core/`, `renderers/`, `extractors/`, `transforms/`, `validators/`)
- Shared types: API contracts defined once, used by both frontend (TypeScript) and backend (Pydantic)

### Naming
- Backend: snake_case for modules, functions, variables. PascalCase for classes.
- Frontend: PascalCase for components. camelCase for functions, variables, props.
- Database: snake_case for tables and columns.
- API: camelCase for JSON keys (frontend convention wins at the API boundary).

### Testing
- Every renderer, extractor, and transform gets its own test file with fixture-based tests
- Integration tests use curated template + data file combinations
- LLM tests use mocked responses — never hit real APIs in CI
