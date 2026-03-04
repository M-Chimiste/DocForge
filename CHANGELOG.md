# Changelog

All notable changes to DocForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- Plugin architecture with entry point discovery for renderers, extractors, and transforms
- `GET /api/v1/plugins` endpoint for listing discovered plugins
- Example plugin packages: markdown renderer, XML extractor, currency transform
- Error catalog with remediation hints for all user-facing errors
- Keyboard shortcuts for the document editor (Ctrl+S save, Ctrl+Shift+E export, etc.)
- Accessibility improvements across all frontend components (aria labels, skip-to-content, focus management)
- In-app onboarding flow and help tooltips
- Server-side pagination for data preview
- Collapsible sections in template analysis view
- MkDocs documentation site with user guide, API reference, and plugin development guide
- PyPI packaging with bundled frontend (`pip install docforge && docforge serve`)
- `docforge serve` CLI command for starting the web server
- Production multi-stage Dockerfile
- Community files (CONTRIBUTING, CODE_OF_CONDUCT, issue/PR templates)
- Additional example templates: financial report, project status, compliance document

## [0.4.0] - Phase 4: Document Editor

### Added
- TipTap-based rich text editor for reviewing generated documents
- Accept/Reject/Regenerate workflow for LLM-generated content
- Low-confidence marker flagging with visual indicators
- Table editing in the editor (cells, rows, columns)
- Editor API endpoints (GET/PUT document, regenerate section, export)
- .docx roundtrip (docx to editor to docx) with formatting preservation
- Editor section tree navigation
- Marker details panel with metadata display

## [0.3.0] - Phase 3: LLM Integration

### Added
- LLM renderer with section-scoped context assembly
- Broadening signal detection for cross-section prompts
- LiteLLM integration supporting local and cloud LLM providers
- Per-project LLM configuration stored in database
- LLM-based data extraction with schema validation
- SSE generation progress streaming
- Context scope display in mapping panel
- LLM connection test endpoint

## [0.2.0] - Phase 2: Full Data Pipeline

### Added
- Extended data ingestion: Text, Word, PowerPoint, PDF, YAML extractors
- Transform pipeline: rename, filter, sort, date format, number format, computed fields
- Auto-resolution engine with fuzzy matching and confidence scoring
- Conditional sections (include/exclude based on data presence or conditions)
- Text renderer for multi-paragraph content injection
- Mapping validation and output validation
- Generation reporting with per-marker results
- Project persistence with SQLite (CRUD, generation history, export/import)
- Complete mapping GUI with transforms and confidence display
- Data preview panel

## [0.1.0] - Phase 1: Foundation

### Added
- Template parser with red text detection (exact #FF0000 at run level)
- Section detection from heading styles (Heading 1, Heading 2, etc.)
- Skeleton table detection with header preservation
- Red text classification rule chain: sample data, variable placeholder, LLM prompt
- Placeholder renderer for variable substitution
- Table renderer for skeleton table population
- Excel, CSV, and JSON data extractors
- FastAPI backend with project and generation APIs
- React frontend with template upload, analysis view, and basic mapping
- CLI commands: `docforge analyze` and `docforge generate`
- Docker Compose deployment (backend + frontend)
- Demo template (Quarterly Report) with sample data files
