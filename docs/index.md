# DocForge

**Template-driven document generation engine with a web-based interface.**

DocForge is an open-source framework that turns Microsoft Word templates into automated document generation pipelines. Authors write instructions in red-formatted text (`#FF0000`) directly inside `.docx` templates -- DocForge parses those instructions, maps them to data sources, optionally calls an LLM for content generation, and produces finished documents ready for review in a built-in editor.

## Why DocForge?

Across regulated industries, consulting, finance, and enterprise operations, teams keep rebuilding the same document generation pipeline with minor variations. Template parsing, data ingestion, table population, section assembly, formatting preservation -- the logic is 80%+ identical every time, but every project starts from scratch. DocForge makes this a solved problem.

## Key Features

- **Red-text templates** -- Author templates in Word using red text as instructions. No special syntax to learn; just write what you want in red.
- **Automatic data mapping** -- Upload data files (Excel, CSV, JSON) and DocForge auto-resolves which data goes where using fuzzy matching with confidence scoring.
- **LLM integration** -- Optionally use any LLM provider (OpenAI, Anthropic, local models via LiteLLM) to generate content for instruction markers.
- **Built-in editor** -- Proof and refine generated documents in a web-based WYSIWYG editor before exporting.
- **Plugin architecture** -- Extend DocForge with custom renderers, extractors, and transforms via Python entry points.
- **Zero-config LLM mode** -- Fully functional without any LLM API keys. LLM features degrade gracefully.
- **Docker deployment** -- Clone, `docker compose up`, and run the demo with zero configuration.

## How It Works

1. **Author** a template in Word -- use red text for LLM instructions and data placeholders
2. **Upload** the template and data files into DocForge
3. **Review** the auto-resolved mappings in the web GUI
4. **Generate** the document -- data populates tables, LLM fulfills instructions, placeholders get substituted
5. **Proof** in the built-in editor -- review LLM content, flag low-confidence items, edit text and tables
6. **Export** the final `.docx`

## Who Is It For?

- **AI Engineers** building document generation workflows who want a reusable framework
- **Business Users** who author templates in Word and want a visual tool for mapping data and generating documents
- **Developers** looking to integrate or extend document generation for their own domains
- **Technical Program Managers** evaluating tools for their teams

## Quick Links

- [Installation](installation.md) -- Get DocForge running locally or with Docker
- [Quickstart](quickstart.md) -- Generate your first document in 5 minutes
- [User Guide](user-guide/templates.md) -- Learn how to author templates and use every feature
- [API Reference](api/overview.md) -- Full REST API documentation
- [Plugin Development](plugins/overview.md) -- Extend DocForge with custom plugins
- [Contributing](contributing/architecture.md) -- Understand the codebase and contribute

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + TypeScript, Material UI, Vite |
| Backend | Python 3.12, FastAPI, uvicorn |
| Document Engine | python-docx, lxml |
| Data Processing | pandas, openpyxl |
| LLM Integration | LiteLLM (OpenAI, Anthropic, local models, and more) |
| Storage | SQLite + SQLAlchemy 2.0 |
| Deployment | Docker / Docker Compose |

## License

DocForge is released under the MIT License.
