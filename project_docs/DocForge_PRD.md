# DocForge — Product Requirements Document

**Project Name:** DocForge
**Author:** Christian Merrill (Theseus Research)
**Version:** 1.0
**Date:** March 3, 2026
**Status:** Approved

---

## 1. Executive Summary

DocForge is an open-source, template-driven document generation application with a visual interface for configuring, generating, and proofing output documents. It takes a formatted .docx template — where red-formatted text serves as placeholder markers and LLM prompt injection points — combines it with structured and unstructured data inputs, and produces a fully populated, publication-ready document while preserving all original formatting, styles, and layout.

The application includes a web-based GUI for verifying auto-resolved data source mappings, configuring generation parameters, and a document editor for proofing, editing text and tables, and reviewing LLM-generated content before final export.

The project is born from a recurring pain point: every new document generation workflow requires rebuilding fundamentally the same pipeline with minor variations. DocForge abstracts the common patterns into a reusable, extensible framework that can be demonstrated end-to-end and adapted to new use cases with minimal effort.

---

## 2. Problem Statement

Across regulated industries, consulting, finance, and enterprise operations, teams repeatedly build bespoke document generation systems that share 80%+ of the same underlying logic: template parsing, data ingestion, table population, section assembly, and formatting preservation. Each new project reinvents these components, leading to duplicated effort, inconsistent quality, and fragile one-off solutions that are difficult to maintain or hand off.

There is no lightweight, open-source tool that handles the full pipeline from template definition through data ingestion to formatted document output — particularly one that can gracefully handle the mix of structured data (spreadsheets, databases) and unstructured content (Office documents, text narratives, extracted PDF content) that real-world document generation demands. Existing solutions either require expensive commercial licenses, lack LLM integration for intelligent content extraction, or provide no visual interface for non-developers to configure and proof documents.

---

## 3. Vision and Goals

**Vision:** A single, composable application that makes document generation a solved problem — so teams can focus on their domain logic rather than plumbing.

**Primary Goals:**

- Provide a reusable, open-source document generation application with a web-based GUI for verification, configuration, and proofing
- Use red-formatted text in templates as a natural, author-friendly marker system that defaults to LLM prompt injection — the template drives the generation logic, the GUI verifies it
- Support mixed data inputs: structured (Excel, CSV, JSON), semi-structured (YAML), and unstructured (Word, PowerPoint, PDF, plain text)
- Preserve all formatting, styles, headers, footers, and page layout from the source template
- Include a built-in document editor for reviewing and editing generated output before final export
- Be demonstrable end-to-end with a single compelling example workflow
- Be modular enough that components can be extracted and used independently

**Non-Goals (v1):**

- Real-time collaborative editing
- PDF output generation (focus on .docx; PDF conversion can be a follow-on)
- Multi-language template support
- Full-featured word processor (the editor is for proofing, not authoring)
- Image injection into placeholders (charts, logos, generated images)
- Multi-document batch generation from a single template (single document generation per run; batch can be revisited if the project moves toward enterprise use)

---

## 4. User Personas

### 4.1 — The AI Engineer (Primary)

An AI/ML engineer or data scientist who is tasked with building document generation workflows. They have Python experience, understand LLM integration patterns, and are frustrated by rebuilding the same pipeline for every new use case. They want a framework they can configure and extend, and a working demo they can show stakeholders.

### 4.2 — The Business User

A non-developer who needs to configure document generation by authoring templates in Word (using red text for placeholders), mapping data sources through the GUI, and proofing/editing generated output before distribution. They care about visual workflow and output quality, not code.

### 4.3 — The Technical Program Manager

Needs to understand what the system does, see a working demo, and evaluate whether it fits their team's needs. They care about the end-to-end workflow visibility, time savings, and the quality of the output document.

### 4.4 — The Developer

A developer who discovers the project on GitHub, wants to understand the architecture quickly, and integrate or extend it for their own domain (legal docs, financial reports, clinical study reports, etc.). They care about clean APIs, good documentation, and the ability to embed DocForge's capabilities into their own applications.

---

## 5. Core Concepts

### 5.1 — Template

A .docx file that serves as the source of truth for document structure, formatting, and generation logic. It contains:

- **Sections:** Named regions of the document defined by heading styles (Heading 1, Heading 2, etc.)
- **Skeleton Tables:** Tables with headers defined but no data rows — these define the schema for data that will be injected. Nested tables (tables within tables) are supported and parsed independently.
- **Red Text Markers:** Any text formatted in red font color serves as an instruction to the system. The system detects red text by matching MS Word's standard "Red" font color (RGB `#FF0000`). A configurable color picker for non-standard marker colors may be added in a future release. Red text is treated as **LLM prompt injection by default** — specific instructions that guide the language model on what content to generate. The system classifies red text into the following categories:
  - **LLM prompt instructions (default)** — red text is treated as a directive to the LLM. The text itself is the prompt, providing specific instructions on what to generate (e.g., `Summarize the key findings from the source data in 2-3 paragraphs`, `List the top 5 risks identified in the project status data`). The LLM uses the mapped data context to fulfill the instruction.
  - **Variable placeholders** — short, label-like red text that clearly represents a single data field to be populated with a mapped value (e.g., `Project Name`, `Report Date`, `Author`). The system identifies these by their brevity and noun/label structure — any red text that is not a clear instruction defaults to LLM prompt.
  - **Table data references** — red text in a table header, caption, or data rows indicating which data source populates the table. If the user provides sample data rows in red text within a skeleton table, the system shall attempt to infer the expected data structure and column mapping from those sample values when a data source is attached
- **Static Content:** Text, images, and formatting in non-red colors that should pass through unchanged

### 5.2 — Data Source Mapping (Template-Primary, GUI-Verified)

The template is the primary driver for data mapping. Red text in the template is authored to be self-describing — the instructions themselves tell the system what data to use and how. The GUI serves as a verification and sanity-checking layer where users can review auto-resolved mappings, override classifications, make corrections, and handle edge cases.

**Template-Driven (Primary Workflow):**

The template author writes red text that contains enough context for the system to resolve data sources automatically. For example:
- A red text LLM prompt reading `Using the data from quarterly_metrics.xlsx, summarize the key performance trends` tells the system both what to do (summarize) and where to get the data (quarterly_metrics.xlsx)
- A red text variable placeholder reading `Project Name` is matched to a field in the uploaded data sources by name
- A skeleton table with red sample data rows provides structural hints for column mapping

**GUI Verification (Secondary Workflow):**

1. User loads a template and uploads data source files
2. System parses the template, classifies red text markers, and auto-resolves mappings where possible based on template context and data source contents
3. GUI displays the resolved mappings for user review — highlighting confidence levels, ambiguous matches, and unresolved markers
4. User confirms, corrects, or manually maps any remaining items
5. User configures any transformations (sorting, filtering, formatting) through the GUI
6. The mapping configuration is stored in a local project database, allowing users to return to a template and generate additional documents with new data files over time. Projects persist across sessions and can be exported/imported for sharing between users

### 5.3 — Data Sources

Input files that provide content for the document. Supported formats include:

- **Structured:** Excel (.xlsx, .xls), CSV, TSV, JSON
- **Semi-structured:** YAML, key-value text files
- **Unstructured Office Documents:** Word (.docx), PowerPoint (.pptx) — content extracted via parsing and/or LLM
- **Other Unstructured:** PDF (via parsing and/or LLM extraction), plain text files

### 5.4 — Renderers

Pluggable components that handle specific output tasks: table population, text injection, LLM-generated content insertion, conditional section inclusion/exclusion, and computed fields.

### 5.5 — Document Editor

A built-in proofing and editing interface that allows users to review the generated document, edit text with full formatting controls, edit table content and structure, accept or reject LLM-generated content, and finalize the document before export. Image manipulation is out of scope.

---

## 6. Core Workflows

### 6.1 — Template Authoring (External)

The user authors their template in Microsoft Word or compatible editor:

1. Write the document with all desired formatting, styles, headers, footers, and layout
2. Add section headings using Word's built-in heading styles
3. Create skeleton tables with formatted headers (no data rows)
4. Format any placeholder text or LLM instructions in **red font color**
5. Save as .docx

### 6.2 — Project Setup (GUI)

```
[1] User opens DocForge application
              ↓
[2] User loads template (.docx)
              ↓
[3] System parses template → discovers:
      - Sections (from headings)
      - Red text markers (LLM prompts by default, variable placeholders, sample data)
      - Skeleton tables
              ↓
[4] User uploads / references data source files
              ↓
[5] System auto-resolves mappings from template context:
      - Red text referencing specific files/data → auto-mapped
      - Variable placeholders → matched by name against data source fields
      - Skeleton tables with sample data → column mapping inferred
              ↓
[6] GUI displays resolved mappings for user verification:
      - Confirmed mappings shown with green indicators
      - Ambiguous or low-confidence mappings flagged for review
      - Unresolved markers highlighted for manual mapping
              ↓
[7] User reviews, corrects, and configures transforms as needed
              ↓
[8] User saves project to database
```

### 6.3 — Document Generation

```
[1] User triggers "Generate" from GUI
              ↓
[2] Engine loads template + project configuration
              ↓
[3] Data ingestion:
      - Structured sources → parsed into DataFrames
      - Unstructured sources (docx, pptx, pdf, txt) → extracted text/content
      - LLM extraction (if configured) → structured data from unstructured sources
              ↓
[4] Rendering:
      - Variable placeholders (red text) → replaced with mapped values,
        formatted to match surrounding style
      - LLM prompts (red text) → sent to LLM with mapped context,
        response injected
      - Skeleton tables → populated with data rows preserving header formatting
      - Conditional sections → included/excluded based on data presence
              ↓
[5] Output document written (.docx)
              ↓
[6] Generation report produced (what was populated, warnings,
      LLM usage, low-confidence mappings flagged for review)
              ↓
[7] Document opens in editor for proofing — LLM content and
      low-confidence items highlighted for user review
```

### 6.4 — Document Proofing and Editing (GUI)

```
[1] Generated document displayed in editor view
              ↓
[2] User reviews content:
      - LLM-generated sections highlighted for review
      - Low-confidence auto-resolved mappings flagged for review
      - Any unresolved markers flagged
      - Formatting preserved from template
              ↓
[3] User can:
      - Edit text directly
      - Accept/reject LLM-generated content
      - Regenerate specific sections with modified prompts
      - Add comments or annotations
              ↓
[4] User finalizes and exports final .docx
```

---

## 7. Functional Requirements

### 7.1 — Template Parsing

- **FR-01:** System shall parse a .docx template and identify all named sections based on heading styles (Heading 1, Heading 2, etc.)
- **FR-02:** System shall identify skeleton tables by detecting tables with header rows but zero or minimal data rows, including nested tables (tables within tables)
- **FR-02a:** System shall support nested table structures, parsing and populating inner tables independently while preserving the outer table's layout and formatting
- **FR-03:** System shall identify all red-formatted text runs as markers by matching MS Word's standard Red font color (RGB `#FF0000`). Red text is classified as **LLM prompt by default**. The system shall only classify red text as a variable placeholder if it matches short, label-like patterns (e.g., 1-3 words, noun/label structure). Red text within table data rows shall be classified as sample data for column mapping inference. Users may override any classification in the GUI.
- **FR-04:** System shall generate a template analysis report listing all discovered sections, markers, and tables — displayed in the GUI for mapping

### 7.2 — Data Source Mapping (Template-Primary, GUI-Verified)

- **FR-05:** System shall auto-resolve data source mappings from template context where red text contains explicit references to file names, data fields, or descriptive instructions that can be matched against uploaded data sources
- **FR-05a:** System shall match variable placeholder names against column headers, field names, and keys in uploaded data sources, presenting best-match candidates ranked by confidence
- **FR-06:** GUI shall display the template structure as a navigable tree/list showing sections, red text markers (with classification type), and skeleton tables, along with auto-resolved mapping status (confirmed, ambiguous, unresolved)
- **FR-07:** GUI shall allow drag-and-drop or selection-based mapping for manual override or resolution of any marker or table
- **FR-08:** GUI shall support per-mapping transformation configuration: column renaming, filtering, sorting, date formatting, number formatting
- **FR-09:** System shall persist project configurations in a local database (SQLite), allowing users to reuse templates with new data files across sessions. Projects shall support export/import for sharing between users
- **FR-10:** System shall validate mappings and report mismatches (unmapped markers, missing data sources, schema mismatches) in the GUI before generation

### 7.3 — Data Ingestion

- **FR-11:** System shall read Excel files (.xlsx, .xls) with support for named sheets and named ranges
- **FR-12:** System shall read .csv and .tsv files with configurable delimiters and encoding
- **FR-13:** System shall read JSON files and extract data from specified paths (JSONPath or dot notation)
- **FR-14:** System shall read plain text files for section content injection
- **FR-15:** System shall extract text content from Word documents (.docx) including body text, tables, and headers
- **FR-16:** System shall extract text content from PowerPoint files (.pptx) including slide text, notes, and table content
- **FR-17:** System shall extract text content from PDF files via text parsing and/or OCR
- **FR-18:** System shall optionally use a configurable LLM to extract structured data from any unstructured source per a user-defined extraction schema

### 7.4 — Rendering

- **FR-19:** System shall replace red text variable placeholders with mapped values, removing the red formatting and applying the surrounding paragraph's style
- **FR-20:** System shall send red text LLM prompts to the configured LLM with context scoped to the **section containing the prompt** by default — only data sources mapped to that section are included. If the prompt explicitly references broader scope (e.g., "summarize all project data," "provide an executive summary covering all sections"), the system shall expand context to include all relevant mapped data sources. The resolved context scope for each LLM prompt shall be displayed in the GUI mapping panel, allowing the user to expand or narrow it during review.
- **FR-21:** System shall populate skeleton tables by appending data rows while preserving the header row formatting and table styles
- **FR-21a:** When a skeleton table contains sample data rows in red text, the system shall infer column mapping and data structure from those sample values as a best-effort first guess. The inferred mapping shall be presented to the user in the mapping panel for confirmation, where users can override column assignments and add detail to the data transformation (sorting, filtering, formatting, computed fields)
- **FR-21b:** System shall support rendering nested tables (tables within tables), populating each inner table from its mapped data source independently while preserving the outer table structure
- **FR-22:** System shall apply cell-level formatting rules configured in the GUI (bold, italic, number format, conditional highlighting)
- **FR-23:** System shall inject multi-paragraph text content into designated sections while preserving surrounding formatting
- **FR-24:** System shall conditionally include or exclude entire sections based on data presence or GUI-configured conditions
- **FR-25:** System shall support computed fields (e.g., row totals, date calculations) configured in the GUI

### 7.5 — Document Editor

- **FR-26:** System shall display the generated document in a WYSIWYG-approximate editor view preserving formatting, tables, and layout
- **FR-27:** Editor shall support text editing: insert, delete, modify text within paragraphs, and apply formatting changes (bold, italic, underline, font size, font color)
- **FR-27a:** Editor shall support table editing: add/remove rows and columns, edit cell content, and modify cell-level formatting
- **FR-28:** Editor shall highlight LLM-generated content distinctly (e.g., light background color) so the user can identify what needs review
- **FR-28a:** Editor shall flag low-confidence auto-resolved mappings in the generated output (e.g., variable placeholders matched with low confidence, ambiguous table column mappings) with a distinct visual indicator, allowing the user to review and correct them alongside LLM-generated content. Low-confidence items shall not block generation.
- **FR-29:** Editor shall allow the user to accept or reject individual LLM-generated sections
- **FR-30:** Editor shall allow the user to select a section and trigger re-generation with an optionally modified prompt
- **FR-31:** Editor shall flag any unresolved red text markers as warnings
- **FR-32:** Editor shall support export of the finalized document as .docx

### 7.6 — Output

- **FR-33:** System shall output a valid .docx file that preserves all template formatting including headers, footers, page numbers, styles, fonts, and page layout
- **FR-34:** System shall support an output validation mode that checks the generated document for completeness (no unresolved red text, no empty required sections)
- **FR-35:** System shall generate a generation report (viewable in GUI and exportable as JSON) documenting what was populated, what was skipped, LLM calls made, and any warnings

---

## 8. Non-Functional Requirements

- **NFR-01:** Document generation (excluding LLM calls — both cloud API and local model inference) shall complete in under 10 seconds for a typical document (20 pages, 5 tables, 10 placeholders) on commodity hardware. Local model inference time is hardware-dependent and explicitly excluded from this performance target.
- **NFR-02:** Application shall be deployable via `docker compose up` with minimal configuration, or installable via `pip install docforge` for the backend with a pre-built frontend bundle
- **NFR-03:** System shall run on Python 3.10+ on Linux, macOS, and Windows
- **NFR-04:** System shall provide clear, actionable error messages for all failure modes, displayed in the GUI
- **NFR-05:** System shall be fully usable without any LLM or API keys — LLM features gracefully degrade to manual entry
- **NFR-06:** All core functionality shall have >90% test coverage
- **NFR-07:** GUI shall be responsive and usable on screens 1280x720 and above
- **NFR-08:** Project files shall be portable across operating systems and shareable between users
- **NFR-09:** System shall be containerized (Docker) for consistent deployment and development environments

---

## 9. Technical Architecture

### 9.1 — Technology Stack

- **Language:** Python 3.10+ (backend), TypeScript (frontend)
- **Frontend Framework:** React with a modern component library (e.g., shadcn/ui, Ant Design, or Material UI) for a polished, responsive web-based interface
- **Backend Framework:** FastAPI for the REST API layer serving the React frontend
- **Document Engine:** python-docx (primary), with lxml for advanced XML manipulation
- **Presentation Parsing:** python-pptx for PowerPoint content extraction
- **Data Processing:** pandas for tabular data, openpyxl for Excel reading
- **PDF Processing:** pymupdf (fitz) for PDF text extraction, optional pytesseract for OCR
- **LLM Integration (optional):** LiteLLM for provider-agnostic LLM access supporting local model servers (LM Studio, Ollama) and frontier cloud providers (OpenAI, Anthropic, Google, Anthropic via AWS Bedrock)
- **Document Editor Component:** Web-based rich text editor (TipTap or ProseMirror) embedded in the React frontend
- **Project Storage:** SQLite database for local project persistence, with export/import for portability
- **Containerization:** Docker / Docker Compose for packaging the full stack (backend + frontend + database)
- **Testing:** pytest with fixtures for template/data combinations

### 9.2 — Module Architecture

```
docforge/
├── frontend/                       # React web application
│   ├── src/
│   │   ├── components/
│   │   │   ├── TemplatePanel.tsx    # Template structure viewer
│   │   │   ├── MappingPanel.tsx     # Data source mapping interface
│   │   │   ├── EditorPanel.tsx      # Document proofing editor (TipTap/ProseMirror)
│   │   │   ├── GenerationPanel.tsx  # Generation controls and progress
│   │   │   ├── MarkerTree.tsx       # Template marker tree view
│   │   │   ├── DataSourceList.tsx   # Data source file list
│   │   │   ├── MappingWidget.tsx    # Individual mapping configuration
│   │   │   └── ReportViewer.tsx     # Generation report display
│   │   ├── pages/
│   │   │   ├── ProjectDashboard.tsx # Project list and management
│   │   │   └── WorkspacePage.tsx    # Main workspace layout
│   │   └── api/                     # API client layer
│   └── package.json
├── backend/
│   ├── api/                         # FastAPI routes
│   │   ├── projects.py              # Project CRUD endpoints
│   │   ├── templates.py             # Template upload and parsing endpoints
│   │   ├── generation.py            # Document generation endpoints
│   │   └── llm.py                   # LLM configuration and invocation endpoints
│   ├── core/
│   │   ├── template_parser.py       # Parse .docx, extract sections/tables/red text
│   │   ├── project.py               # Project configuration model
│   │   ├── data_loader.py           # Ingest data from various file formats
│   │   └── engine.py                # Orchestration: wire everything together
│   ├── renderers/
│   │   ├── base.py                  # Abstract renderer interface
│   │   ├── table_renderer.py        # Populate skeleton tables with data
│   │   ├── text_renderer.py         # Inject text content into sections
│   │   ├── placeholder_renderer.py  # Red text variable substitution
│   │   ├── llm_renderer.py          # LLM prompt execution and injection
│   │   └── conditional.py           # Section include/exclude logic
│   ├── extractors/                  # Content extraction from unstructured sources
│   │   ├── base.py                  # Extractor interface
│   │   ├── docx_extractor.py        # Extract content from Word documents
│   │   ├── pptx_extractor.py        # Extract content from PowerPoint files
│   │   ├── pdf_extractor.py         # Extract content from PDFs
│   │   ├── text_extractor.py        # Plain text loading
│   │   └── llm_extractor.py         # LLM-based structured extraction
│   ├── transforms/
│   │   ├── base.py                  # Transform interface
│   │   ├── column_ops.py            # Rename, filter, sort, format
│   │   └── computed.py              # Computed fields and aggregations
│   ├── validators/
│   │   ├── mapping_validator.py     # Validate data-to-template mappings
│   │   └── output_validator.py      # Validate generated document completeness
│   ├── db/                          # Database layer
│   │   ├── models.py                # SQLAlchemy/SQLite models
│   │   └── repository.py            # Project and generation history queries
│   └── utils/
│       ├── docx_helpers.py          # Low-level python-docx utilities
│       ├── red_text.py              # Red text detection and classification
│       └── formatting.py            # Format conversion utilities
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### 9.3 — Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                DocForge Web Application                  │
│           (React Frontend + FastAPI Backend)             │
│                                                         │
│  ┌─ Template Panel ────────┐                            │
│  │  Sections, Tables,      │                            │
Template (.docx) ──────────→│  Red Text Markers          │                            │
│  └─────────────────────────┘                            │
│              │                                          │
│  ┌─ Mapping Panel ─────────┐                            │
Data Files ────────────────→│  Source → Target            │                            │
(.xlsx, .csv, .json, .docx, │  Transforms                │                            │
 .pptx, .pdf, .txt)         │  LLM Config                │                            │
│  └─────────────────────────┘                            │
│              │                                          │
│         [Generate]                                      │
│              │                                          │
│              ▼                                          │
│  ┌─ Engine ────────────────┐                            │
│  │  Parse Template         │                            │
│  │  Load & Extract Data    │                            │
│  │  Render Content         │                            │
│  │  Write Output           │                            │
│  └─────────────────────────┘                            │
│              │                                          │
│              ▼                                          │
│  ┌─ Editor Panel ──────────┐                            │
│  │  WYSIWYG Preview        │                            │
│  │  LLM Content Review     │                            │
│  │  Edit / Accept / Reject │                            │
│  │  Export Final .docx     │                            │
│  └─────────────────────────┘                            │
└─────────────────────────────────────────────────────────┘
```

### 9.4 — Red Text Processing Pipeline

```
Template Parsing
       │
       ▼
Identify all red-formatted text runs in the document
       │
       ▼
Classify each red text run:
       │
       ├── Red text within skeleton table data rows
       │       → Classified as SAMPLE_DATA (used for column mapping inference)
       │
       ├── Short label-like text (1-3 words, noun/label structure,
       │   e.g., Project Name, Report Date, Author)
       │       → Classified as VARIABLE_PLACEHOLDER
       │
       └── All other red text (DEFAULT)
               → Classified as LLM_PROMPT (instruction to guide the LLM)
       │
       ▼
Display classified markers in GUI for user review and mapping
       │
       ▼
Auto-resolve mappings from template context:
       - Match file/data references in LLM prompt text to uploaded sources
       - Scope LLM context to containing section by default
         (expand to all sources if prompt explicitly references broader scope)
       - Match variable placeholder names to data source fields
       - Infer column mappings from sample data in skeleton tables
       │
       ▼
User verifies/overrides classifications and mappings in GUI
```

---

## 10. GUI Wireframe Descriptions

### 10.1 — Main Window Layout

The application uses a multi-panel layout:

- **Left Panel — Template Structure:** Tree view showing the document hierarchy — sections (from headings), red text markers (with type icons: variable vs. LLM prompt), and skeleton tables. Clicking any item scrolls the preview to that location.
- **Center Panel — Document Preview / Editor:** Shows the template initially, then the generated document. Switches between read-only preview mode and edit mode. Red text markers are visually prominent. After generation, LLM-generated content is highlighted with a subtle background color.
- **Right Panel — Data & Mapping:** Lists uploaded data source files with file type icons. Below, shows the mapping configuration for the currently selected template marker. Includes data preview (first N rows for tabular data, text snippet for unstructured).
- **Bottom Bar — Actions & Status:** Generate button, progress bar during generation, status messages, and export button.

### 10.2 — Mapping Configuration

When a user selects a red text marker or skeleton table in the left panel:

- The right panel shows the auto-resolved mapping (if any) with a confidence indicator, plus a mapping form for override or manual configuration
- **For LLM prompts (default):** shows the red text as the prompt, auto-resolved context scope (section-level by default, with option to expand to all sources or narrow to specific files), configure model (dropdown), temperature, max tokens
- **For variable placeholders:** shows auto-matched data source field with confidence score, dropdown to override with a different data source → sheet/path → specific cell or column
- **For skeleton tables:** shows auto-inferred column mapping (from sample data if present), data source → sheet selector, column mapping grid (template column headers on left, source columns on right), plus transform configuration (sort, filter, format)

### 10.3 — Editor View

After generation, the center panel switches to editor mode:

- Document rendered with formatting approximating the final .docx output
- LLM-generated sections have a colored left border and subtle background highlight
- Low-confidence auto-resolved mappings flagged with a distinct indicator for post-generation review
- Hovering over LLM content or low-confidence items shows a floating toolbar: Accept, Reject, Regenerate, Edit Mapping
- Unresolved red text markers shown with warning icon
- Text editing: click to place cursor, type to edit, formatting toolbar (bold, italic, underline, font size, font color)
- Table editing: click into table cells to edit content, add/remove rows and columns, modify cell formatting
- "Export" button produces the final .docx

---

## 11. Demo Scenario

For the initial demonstration, DocForge will generate a **Quarterly AI Operations Report** using:

- **Template:** A formatted .docx with company branding, table of contents, section headings (Executive Summary, Key Metrics, Project Status, Resource Allocation, Recommendations), skeleton tables for metrics and project status, and red-formatted placeholder text for dates, authors, project names, and an LLM prompt for the executive summary
- **Data Sources:** An Excel file with KPI metrics across sheets, a CSV with project status data, a PowerPoint deck with last quarter's strategy slides (used as context for the LLM summary), and a plain text file with team roster data
- **Workflow:**
  1. User opens DocForge, loads the template
  2. System identifies 6 red text markers (3 variables, 2 LLM prompts, 1 table reference) and 2 skeleton tables
  3. User uploads data files — system auto-resolves most mappings from template context
  4. User reviews mappings in GUI, confirms auto-resolved items, manually maps any remaining
  5. User clicks Generate — document populates in ~5 seconds (plus LLM call time)
  6. User reviews in the editor, edits one LLM-generated paragraph, adjusts a table, accepts the rest
  7. User exports final .docx
- **Output:** A fully formatted, publication-ready document with all tables populated, all red text resolved, and all sections filled

This demo should be completable in under 10 minutes from application launch to exported document.

---

## 12. Release Plan

### v0.1 — Foundation

- Template parser (sections, tables, red text marker detection and classification)
- Red text variable placeholder substitution
- Basic table population from Excel/CSV
- Minimal web UI: template viewer, basic mapping interface, generate button
- Docker Compose setup for local deployment
- CLI fallback with `generate` and `analyze` commands
- Single demo workflow

### v0.2 — Full Data Pipeline

- Complete GUI mapping interface with drag-and-drop
- Transform pipeline (sort, filter, rename, format) configurable via GUI
- Text section injection from unstructured sources
- Word and PowerPoint content extraction
- Conditional sections
- Project database persistence (SQLite) with export/import
- Output validation and generation report

### v0.3 — LLM Integration

- LLM prompt marker detection and execution
- Provider-agnostic LLM configuration: local servers (LM Studio, Ollama) and cloud providers (OpenAI, Anthropic, Google, Anthropic via AWS Bedrock)
- Context assembly from mapped data sources
- LLM-based extraction from unstructured sources

### v0.4 — Document Editor

- WYSIWYG-approximate editor view
- LLM content highlighting and accept/reject workflow
- Section-level regeneration
- Text editing with formatting controls (bold, italic, underline, font size, font color)
- Table editing: cell content, add/remove rows and columns, cell formatting
- Final export with all edits applied

### v0.5 — Polish & Extensibility

- Plugin architecture for custom renderers, extractors, and transforms
- Comprehensive error messages and troubleshooting guide
- Documentation site
- PyPI package publication
- Community contribution guidelines

---

## 13. Resolved Decisions

1. **Naming:** DocForge is confirmed as the project name.
2. **GUI Framework:** React-based web application with FastAPI backend — modern web UI with better UX support and easier styling.
3. **Red Text Heuristics:** Red text defaults to LLM prompt injection / specific instructions to guide the LLM. Only short label-like text (1-3 words, noun structure) is classified as a variable placeholder. Users can override any classification in the GUI.
4. **Nested Tables:** Supported in v1. The system will parse and populate nested tables (tables within tables) independently.
5. **Image Injection:** Not in scope for v1. Added to non-goals.
6. **Multi-document Batch:** Not in scope for v1. Single document generation per run. Can be revisited for enterprise use.
7. **Editor Depth:** Full editing capabilities including text editing with formatting controls, table editing (add/remove rows and columns, cell content, cell formatting). Image manipulation is excluded.
8. **Template vs. GUI Mapping:** Template-driven is the primary workflow — red text is authored to be self-describing with enough context for the system to auto-resolve data source mappings. The GUI serves as a verification and sanity-checking layer for reviewing, correcting, and overriding auto-resolved mappings.
9. **Red Text Color Tolerance:** Default to MS Word's standard Red (`#FF0000`) with no tolerance range for v1. A configurable color picker can be added later if users need to support non-standard marker colors.
10. **Sample Data Inference:** Best-effort auto-inference from red sample data in skeleton tables, presented to the user in the GUI for confirmation. Users can override any inferred mapping, adjust column assignments, and configure transformations. The goal is a good first guess that the user refines.
11. **Auto-Resolution Confidence:** Low-confidence auto-resolved mappings are flagged **after generation** in the editor view, not before. They do not block the generation step. Low-confidence items are highlighted alongside LLM-generated content for user review. High-confidence mappings proceed without interruption.
12. **LLM Prompt Context Assembly:** LLM context is scoped to the **section** containing the red text prompt by default. If the prompt explicitly references broader scope (e.g., "provide an executive summary covering all sections"), context expands to all mapped data sources. The GUI mapping panel displays the resolved context scope and lets the user expand or narrow it.
