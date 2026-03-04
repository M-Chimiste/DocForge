# DocForge — Phased Implementation Plan

**Project:** DocForge
**Date:** March 3, 2026
**Audience:** Engineering team, project management

---

## Overview

This plan breaks DocForge development into five phases, each delivering a usable increment of the system. Phases are sequenced so that each one builds on the previous — no phase requires rework of completed phases. The goal is a working demo after Phase 1 and a feature-complete product after Phase 4, with Phase 5 focused on extensibility and community readiness.

---

## Phase 1: Foundation

**Goal:** Parse a template, substitute placeholders, populate tables, and output a document — with a minimal web UI and Docker deployment.

### Infrastructure Setup
- Initialize monorepo structure (`frontend/`, `backend/`, `docker-compose.yml`, `Dockerfile`)
- Docker Compose configuration: backend (FastAPI + uvicorn), frontend (React dev server / nginx), shared volume
- SQLite database initialization with project table schema
- CI pipeline: lint, test, build, containerize

### Backend — Template Parser
- `.docx` template parsing with python-docx + lxml
- Section detection from heading styles (Heading 1, Heading 2, etc.)
- Skeleton table detection (tables with headers, zero or minimal data rows)
- Red text detection: exact RGB `#FF0000` match at the run level
- Red text classification: rule chain (sample data → variable placeholder → LLM prompt default)
- Template analysis report: JSON output listing all discovered sections, markers, tables with classifications

### Backend — Basic Renderers
- `PlaceholderRenderer`: substitute variable placeholder red text with mapped values, apply surrounding style
- `TableRenderer`: populate skeleton tables from DataFrames, preserve header formatting and table styles
- Engine orchestration: parse → ingest → render → output pipeline (no LLM, no transforms yet)

### Backend — Data Ingestion (Structured Only)
- Excel reader (.xlsx, .xls) with sheet and named range support
- CSV/TSV reader with configurable delimiters and encoding
- JSON reader with dot-notation path extraction

### Backend — API Layer
- `POST /api/v1/projects` — create project
- `POST /api/v1/templates/analyze` — upload and parse template, return analysis
- `POST /api/v1/projects/{id}/generate` — run generation, return output document
- File upload endpoints for templates and data sources

### Frontend — Minimal Web UI
- Project creation page
- Template upload with drag-and-drop
- Template analysis display: tree view of sections, markers, tables
- Basic mapping interface: select a marker, assign a data source + field
- Generate button with progress indicator
- Download generated .docx

### CLI Fallback
- `docforge analyze --template <path>` — parse template, output analysis JSON
- `docforge generate --template <path> --data <path> --output <path>` — generate document from command line

### Demo Workflow
- Curated demo template (Quarterly Report) with 3 variable placeholders and 2 skeleton tables
- Curated demo data files (Excel with metrics, CSV with project status)
- README with step-by-step instructions for clone → docker compose up → demo

### Exit Criteria
- [ ] Template parser correctly identifies sections, tables, and red text markers in the demo template
- [ ] Placeholder substitution replaces red text with correct values and removes red formatting
- [ ] Table population fills skeleton tables from Excel/CSV with correct data and preserved formatting
- [ ] Web UI displays template analysis and allows basic mapping
- [ ] `docker compose up` brings up the full stack and serves the UI
- [ ] Demo workflow completable in under 5 minutes

---

## Phase 2: Full Data Pipeline

**Goal:** Complete the mapping GUI, add transforms, support all data source formats, add project persistence, and enable template-primary auto-resolution.

### Backend — Extended Data Ingestion
- Plain text reader for section content injection
- Word (.docx) content extractor: body text, tables, headers
- PowerPoint (.pptx) content extractor: slide text, notes, table content
- PDF text extractor via pymupdf, optional OCR via pytesseract
- YAML reader for semi-structured data

### Backend — Transform Pipeline
- Column rename transform
- Filter transform (row filtering by condition)
- Sort transform (single and multi-column)
- Format transforms: date formatting, number formatting (decimals, currency, percentage)
- Computed fields: row totals, date calculations, basic aggregations

### Backend — Auto-Resolution Engine
- Fuzzy matching: variable placeholder names against data source field names
- File reference detection: extract filenames from LLM prompt text, match against uploaded files
- Sample data inference: analyze red text in table data rows, infer column mapping against data source structure
- Confidence scoring: exact match (1.0), fuzzy match (0.5-0.8), structural match (0.6-0.8), no match (0.0)
- Auto-resolution report: per-marker confidence scores, match reasoning

### Backend — Conditional Sections
- Include/exclude sections based on data presence
- Include/exclude based on explicit GUI-configured conditions

### Backend — Text Renderer
- `TextRenderer`: inject multi-paragraph text content into designated sections, preserve surrounding formatting

### Backend — Validation & Reporting
- Mapping validator: check for unmapped markers, missing sources, schema mismatches
- Output validator: check for unresolved red text, empty required sections
- Generation report: JSON documenting what was populated, skipped, warnings, confidence flags

### Backend — Project Persistence
- SQLite schema: projects, generation runs, mapping snapshots
- Project CRUD API endpoints
- Generation history: append-only run records with mapping snapshot, output reference, report
- Project export/import: JSON bundle serialization

### Frontend — Complete Mapping GUI
- Drag-and-drop mapping from data source fields to template markers
- Per-mapping transform configuration panel (sort, filter, rename, format)
- Auto-resolved mapping display with confidence indicators (green/yellow/red)
- Data preview panel: first N rows for tabular data, text snippet for unstructured
- Mapping validation display: warnings, errors, suggestions
- Project save/load from database
- Project dashboard: list projects, open recent, create new

### Exit Criteria
- [ ] All data source formats (Excel, CSV, JSON, YAML, text, Word, PowerPoint, PDF) load and extract correctly
- [ ] Transform pipeline applies sort, filter, rename, format, computed fields
- [ ] Auto-resolution correctly matches placeholders to data fields with appropriate confidence scores
- [ ] Conditional sections include/exclude based on data presence
- [ ] Projects persist across sessions in SQLite
- [ ] Mapping GUI supports drag-and-drop, transforms, and confidence display

---

## Phase 3: LLM Integration

**Goal:** Red text LLM prompts are executed with proper context scoping, using configurable local or cloud LLM providers.

### Backend — LLM Configuration
- LLM provider configuration model: provider type, endpoint, model name, API key reference, temperature, max tokens
- LiteLLM integration: unified API surface for all supported providers
- Provider connection test endpoint: validate credentials and reachability
- Per-project LLM configuration, stored in database

### Backend — LLM Renderer
- `LLMRenderer`: assemble context, format prompt, call LLM, inject response into document
- Section-scoped context assembly: only include data mapped to the containing section
- Broadening signal detection: heuristic scan for "all sections," "entire document," "executive summary," "overall," cross-section references
- Context scope resolution: default section scope + detected broadening → resolved scope per prompt
- Response injection: replace red text with LLM output, apply surrounding paragraph style
- Error handling: timeout, rate limit, auth failure → fail-forward, record in report, leave red text

### Backend — LLM-Based Extraction
- Schema-driven extraction: user defines expected output schema, LLM extracts structured data from unstructured source
- Extraction validation: check LLM output against expected schema, flag mismatches
- Integrated into the extractor registry alongside file-format extractors

### Backend — Generation Progress
- Server-Sent Events (SSE) endpoint for generation progress
- Per-stage progress updates: parsing, ingestion, rendering (per-marker), validation
- LLM call progress: which prompt is being processed, estimated time based on token count

### Frontend — LLM Configuration
- LLM settings panel: provider selection, endpoint, model, API key (masked), temperature, max tokens
- Connection test button with success/failure feedback
- Per-project LLM settings, saved with project

### Frontend — Context Scope Display
- Mapping panel shows resolved context scope for each LLM prompt
- User can expand (all sources) or narrow (specific files) the scope
- Visual indicator of which data sources are included as context

### Frontend — Generation Progress
- SSE-driven progress bar with per-stage updates
- Per-prompt progress display during LLM rendering stage
- Estimated time remaining based on prompt count and average call duration

### Exit Criteria
- [ ] LLM prompts execute with correct section-scoped context
- [ ] Broadening signals correctly expand context scope
- [ ] Local model servers (LM Studio, Ollama) connect and generate responses
- [ ] Cloud providers (OpenAI, Anthropic, Google, Bedrock) connect and generate responses
- [ ] LLM failures are fail-forward: recorded in report, do not abort generation
- [ ] Generation progress streams to the frontend via SSE
- [ ] System is fully functional with no LLM configured (graceful degradation)

---

## Phase 4: Document Editor

**Goal:** Generated documents are reviewable and editable in a rich web-based editor with LLM content review, low-confidence flagging, table editing, and final export.

### Frontend — Editor Component
- TipTap or ProseMirror integration for rich text editing
- Document rendering: convert generated .docx content to editor-renderable format (HTML/JSON)
- Text editing: insert, delete, modify text within paragraphs
- Formatting toolbar: bold, italic, underline, font size, font color
- Table editing: click into cells, edit content, add/remove rows and columns, cell-level formatting
- Section navigation: click in template tree to scroll editor to that section

### Frontend — LLM Content Review
- LLM-generated sections highlighted with colored left border and subtle background
- Low-confidence auto-resolved mappings flagged with distinct visual indicator
- Floating toolbar on hover: Accept, Reject, Regenerate, Edit Mapping
- Accept: remove highlight, content becomes final
- Reject: revert to original red text marker
- Regenerate: open prompt editor, allow modification, re-run LLM for that section
- Edit Mapping: open mapping panel for the specific marker, allow re-resolution

### Frontend — Unresolved Marker Warnings
- Unresolved red text markers displayed with warning icon
- Click to open mapping panel for manual resolution
- Option to generate again after resolving

### Backend — Editor API
- `GET /api/v1/generations/{id}/document` — return generated document in editor-renderable format
- `PUT /api/v1/generations/{id}/document` — persist editor changes
- `POST /api/v1/generations/{id}/regenerate-section` — re-run LLM for a specific section with optional prompt modification
- `POST /api/v1/generations/{id}/export` — produce final .docx from editor state

### Backend — Export Engine
- Convert editor state back to .docx format preserving all formatting
- Apply accepted edits, remove rejected LLM content, resolve accepted low-confidence items
- Final validation pass: check for remaining unresolved markers, warn if present

### Exit Criteria
- [ ] Generated document renders in the editor with approximate WYSIWYG fidelity
- [ ] LLM-generated content and low-confidence items are visually distinct and reviewable
- [ ] Accept/Reject/Regenerate workflow functions correctly for each flagged item
- [ ] Text editing and formatting changes persist and export correctly
- [ ] Table editing (cells, rows, columns) works and exports correctly
- [ ] Exported .docx preserves all template formatting, edits, and accepted content

---

## Phase 5: Polish & Extensibility

**Goal:** Plugin architecture, comprehensive documentation, error handling polish, and open-source release readiness.

### Plugin Architecture
- Plugin interface for custom renderers: register via entry points or configuration
- Plugin interface for custom extractors: new file format support without forking
- Plugin interface for custom transforms: domain-specific data transformations
- Plugin discovery: scan installed packages for docforge plugin entry points
- Plugin documentation: how to build, register, and distribute a DocForge plugin

### Error Handling & UX Polish
- Comprehensive error messages for all failure modes with suggested remediation
- Troubleshooting guide: common issues and solutions
- Keyboard shortcuts for editor operations
- Accessibility pass: screen reader support, keyboard navigation
- Performance optimization: lazy loading for large templates, pagination for large data previews

### Documentation
- Documentation site (MkDocs or similar): installation, quickstart, user guide, API reference, plugin development
- In-app help: tooltips, onboarding flow for first-time users
- Architecture guide for contributors: system patterns, code conventions, how to add a renderer/extractor

### Distribution
- PyPI package: `pip install docforge` installs backend + bundled frontend
- Docker Hub image: pre-built container for zero-config deployment
- GitHub release automation: version tagging, changelog generation, asset publishing

### Community Readiness
- Contributing guide: code style, PR process, issue templates
- Code of conduct
- Issue and PR templates
- Example templates and data files for common use cases (financial report, project status, compliance document)
- Roadmap: public backlog of planned features and community-requested enhancements

### Exit Criteria
- [ ] At least one custom renderer, extractor, and transform implemented as example plugins
- [ ] Documentation site covers installation, user guide, API reference, and plugin development
- [ ] `pip install docforge` and `docker compose up` both work for fresh installs
- [ ] Published to PyPI and Docker Hub
- [ ] GitHub repo has README, contributing guide, license, issue templates, and CI badges

---

## Phase Dependencies

```
Phase 1 (Foundation)
    │
    ▼
Phase 2 (Data Pipeline)
    │
    ├──────────────────┐
    ▼                  ▼
Phase 3 (LLM)    Phase 4 (Editor)  ← can be parallelized
    │                  │
    └────────┬─────────┘
             ▼
      Phase 5 (Polish)
```

**Parallelization opportunity:** Phases 3 (LLM Integration) and Phase 4 (Document Editor) can be developed in parallel after Phase 2 is complete. The LLM renderer and the editor are independent subsystems that converge only at the "LLM content review in editor" feature — which can be integrated once both are functional.

---

## Estimated Effort

| Phase | Scope | Estimated Duration |
|-------|-------|--------------------|
| Phase 1 — Foundation | Parser, basic renderers, minimal UI, Docker | 3-4 weeks |
| Phase 2 — Data Pipeline | All extractors, transforms, auto-resolution, mapping GUI, persistence | 4-6 weeks |
| Phase 3 — LLM Integration | LLM renderer, context scoping, provider config, progress streaming | 3-4 weeks |
| Phase 4 — Document Editor | Rich text editor, review workflow, table editing, export | 4-5 weeks |
| Phase 5 — Polish & Extensibility | Plugins, docs, distribution, community readiness | 3-4 weeks |
| **Total** | | **17-23 weeks** |

Estimates assume a single full-time engineer. Phases 3 and 4 can be parallelized with a second engineer, compressing the timeline by 3-5 weeks.
