# DocForge — Technical Context

**Project:** DocForge
**Date:** March 3, 2026
**Audience:** Engineers, architects, contributors

---

## 1. System Overview

DocForge is a containerized web application for template-driven document generation. It follows a two-tier architecture: a React/TypeScript frontend communicating via REST API with a Python/FastAPI backend. All document processing, data ingestion, LLM orchestration, and rendering happen server-side. The frontend handles template visualization, mapping verification, document editing, and user interaction.

```
┌──────────────────────────────────────────────────────────────┐
│                        Browser                               │
│  React + TypeScript + TipTap/ProseMirror Editor              │
└──────────────────────┬───────────────────────────────────────┘
                       │ REST API (JSON + file upload)
┌──────────────────────▼───────────────────────────────────────┐
│                    FastAPI Backend                            │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────────┐  │
│  │ Template │ │ Data     │ │ Render   │ │ LLM             │  │
│  │ Parser   │ │ Ingestion│ │ Engine   │ │ Orchestration   │  │
│  └─────────┘ └──────────┘ └──────────┘ └─────────────────┘  │
│  ┌─────────────────┐ ┌──────────────────────────────────┐    │
│  │ SQLite (Projects)│ │ File System (templates, data,    │    │
│  │                  │ │ generated docs)                  │    │
│  └─────────────────┘ └──────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## 2. Technology Choices and Rationale

### Frontend: React + TypeScript

**Why:** Web-based UI provides the best UX flexibility, cross-platform support, and contribution friendliness. React's ecosystem offers mature rich text editors (TipTap/ProseMirror), drag-and-drop libraries, tree view components, and table editing that would require significant custom work in native GUI frameworks.

**Component library:** shadcn/ui, Ant Design, or Material UI — decision deferred to implementation. Priority is a clean, professional interface that doesn't look like a developer tool.

**Key frontend concerns:**
- TipTap or ProseMirror for the WYSIWYG document editor — must support rich text formatting, table editing, and custom decorations (LLM highlights, confidence indicators)
- File upload handling for templates and data sources (multi-file, drag-and-drop)
- Tree view for template structure navigation with real-time status indicators
- Responsive layout targeting 1280x720 minimum

### Backend: Python 3.10+ / FastAPI

**Why:** Python is the natural choice given the document processing ecosystem (python-docx, python-pptx, pymupdf, pandas, openpyxl) and LLM integration landscape (LiteLLM). FastAPI provides async support, automatic OpenAPI docs, and Pydantic model validation with minimal boilerplate.

**Key backend concerns:**
- Document processing is CPU-bound — generation requests should be handled with background tasks or a task queue for responsiveness
- File management: uploaded templates, data files, and generated documents need organized storage with cleanup policies
- LLM calls are I/O-bound and variable-latency — async handling is essential, especially for local model servers

### Document Engine: python-docx + lxml

**Why:** python-docx is the most mature Python library for reading and writing .docx files. It handles styles, tables, headers/footers, and section properties. For edge cases (nested tables, advanced XML manipulation, red text color detection at the run level), direct lxml access to the underlying Open XML gives full control.

**Known limitations:**
- python-docx has limited support for nested tables — custom XML traversal via lxml will be needed
- Complex formatting (tracked changes, embedded objects, SmartArt) may not survive round-trip processing
- Table-of-contents fields are stored as field codes — they won't auto-update without opening in Word

### LLM Integration: LiteLLM

**Why:** LiteLLM provides a single API surface for multiple LLM providers, supporting both cloud and local model servers. This avoids vendor lock-in and lets users bring their own models.

**Supported providers:**
- **Local:** LM Studio (OpenAI-compatible API), Ollama (native API)
- **Cloud:** OpenAI, Anthropic, Google (Gemini), Anthropic via AWS Bedrock

**Design constraints:**
- All LLM features must be optional — the system must be fully functional with zero API keys
- LLM calls are the primary latency variable — the UI must show per-section progress during generation
- Context assembly is section-scoped by default — the system must resolve scope from prompt content and allow user override
- Token usage and cost should be tracked in the generation report

### Data Processing: pandas + openpyxl

**Why:** pandas is the standard for tabular data manipulation in Python. openpyxl handles Excel reading with sheet/range support. Together they cover the structured data pipeline (Excel, CSV, TSV, JSON) with minimal custom code.

**Additional extractors:**
- python-pptx for PowerPoint slide text, notes, and table content
- pymupdf (fitz) for PDF text extraction, with optional pytesseract for OCR on scanned documents
- Plain text reader for narrative content injection

### Storage: SQLite

**Why:** SQLite provides zero-configuration, file-based relational storage that ships with Python. Perfect for single-user or small-team deployments. Project configurations, generation history, and template metadata persist across sessions without requiring an external database server.

**Schema concerns:**
- Projects table: template reference, mapping configuration (JSON), LLM settings, creation/update timestamps
- Generation runs table: project reference, data source snapshots, generation report, output document reference, timestamp
- Export/import: full project serialization to JSON for portability between instances

### Containerization: Docker / Docker Compose

**Why:** Ensures consistent deployment across developer machines, CI/CD, and production-like environments. Simplifies dependency management for the mixed Python + Node stack.

**Compose services:**
- `frontend`: Node build → nginx serving static assets, proxying API calls
- `backend`: Python FastAPI with uvicorn
- Shared volume for file storage (templates, data, outputs)
- SQLite database file on a persistent volume

## 3. Technical Constraints

| Constraint | Impact |
|-----------|--------|
| python-docx nested table support is limited | Custom lxml XML traversal required for FR-02a/FR-21b |
| LLM latency is unpredictable (especially local models) | UI must show per-section progress; generation cannot have a hard timeout |
| .docx formatting fidelity | Complex features (tracked changes, SmartArt, embedded objects) may degrade on round-trip |
| Red text detection relies on exact RGB match (`#FF0000`) | Templates using non-standard reds will miss markers — documented as known limitation with future color picker |
| SQLite is single-writer | Concurrent multi-user access is not supported in v1 — acceptable for the target deployment model |
| TipTap/ProseMirror !== Word rendering | Editor is WYSIWYG-approximate, not pixel-perfect — final output may differ slightly from editor preview |

## 4. Integration Points

### LLM Providers (via LiteLLM)
- Configuration stored per-project in the database
- API keys stored locally (environment variables or config file, never in the database)
- Connection tested on configuration save, with clear error messages for auth failures or unreachable endpoints

### File System
- Uploaded templates and data files stored in a managed directory with project-scoped namespacing
- Generated documents written to an output directory with generation run ID
- Cleanup policy needed for orphaned files from deleted projects

### Export/Import
- Projects serializable to a portable JSON bundle including mapping configuration, LLM settings, and template metadata (but not the template or data files themselves — those are referenced by path)
- Import validates the bundle against the current schema and reports missing file references

## 5. Development Environment

```
# Prerequisites
- Docker + Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.10+ (for backend development)

# Quick start
git clone https://github.com/theseus-research/docforge.git
cd docforge
docker compose up

# Development mode (hot reload)
cd frontend && npm run dev      # React dev server on :5173
cd backend && uvicorn main:app  # FastAPI on :8000
```

## 6. Testing Strategy

| Layer | Framework | Scope |
|-------|-----------|-------|
| Backend unit tests | pytest | Template parser, renderers, extractors, transforms, validators |
| Backend integration tests | pytest + httpx | API endpoints, generation pipeline end-to-end |
| Frontend unit tests | Vitest + React Testing Library | Component behavior, state management |
| Frontend E2E tests | Playwright | Full workflow: upload → map → generate → edit → export |
| LLM integration tests | pytest (mocked) | Prompt assembly, context scoping, response injection — mocked LLM responses |
| Fixture library | Shared | Curated .docx templates, Excel/CSV data files, expected outputs for regression |

Target: >90% coverage on core backend functionality (parsers, renderers, engine).
