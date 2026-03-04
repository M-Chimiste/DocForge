# DocForge

**Template-driven document generation engine with a web-based interface.**

DocForge lets you author `.docx` templates using red-formatted text as instructions. Upload data sources, and DocForge automatically fills in your template — with optional AI-generated content for narrative sections.

## Key Features

- **Template-driven** — Author templates in Microsoft Word. Red text (`#FF0000`) marks where content should be inserted.
- **Multi-format data** — Excel, CSV, JSON, YAML, plain text, Word, PowerPoint, and PDF data sources.
- **Auto-resolution** — Fuzzy-matches template markers to data source fields with confidence scoring.
- **Transform pipeline** — Sort, filter, rename, format dates/numbers, and compute fields before rendering.
- **Optional LLM integration** — AI-generated content via any provider (OpenAI, Anthropic, Ollama, LM Studio, etc.) through LiteLLM.
- **Built-in editor** — Review generated documents in a rich text editor. Accept, reject, or regenerate LLM content.
- **Plugin architecture** — Extend with custom renderers, extractors, and transforms via Python entry points.
- **CLI and API** — Use the web UI, REST API, or command-line interface.

## Quick Start

### With pip

```bash
pip install docforge
docforge serve
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

### With Docker

```bash
docker run -p 8000:8000 docforge/docforge
```

### From source

```bash
git clone https://github.com/m-chimiste/docforge.git
cd docforge
docker compose up
```

The UI is available at `http://localhost:5173` and the API at `http://localhost:8000`.

## Demo

DocForge ships with a demo template and sample data:

```bash
# Analyze a template
docforge analyze --template demo/templates/quarterly_report.docx

# Generate a document
docforge generate \
  --template demo/templates/quarterly_report.docx \
  --data demo/data/quarterly_metrics.xlsx \
  --data demo/data/project_status.csv \
  --data demo/data/config.json \
  --mapping demo/data/mapping.json \
  --output output.docx
```

Additional examples are available in `examples/templates/` covering financial reports, project status reports, and compliance documents.

## How It Works

```
Template (.docx) --> Parse --> Ingest Data --> Render Markers --> Output (.docx)
                                                    |
                                              [Optional LLM]
```

1. **Parse** — DocForge scans the template for red-formatted text, classifying markers as variable placeholders, sample data (table rows), or LLM prompts.
2. **Ingest** — Data sources are loaded and extracted into a unified data store.
3. **Render** — Each marker is resolved: placeholders are substituted, tables are populated, and LLM prompts are executed.
4. **Review** — Open the generated document in the built-in editor to accept, reject, or regenerate content.
5. **Export** — Download the final `.docx` with all formatting preserved.

## Architecture

DocForge is a layered monolith with clean internal boundaries:

```
Frontend (React) --> API (FastAPI) --> Engine (Parser, Renderers) --> Storage (SQLite, FS)
```

- **Backend:** Python 3.12, FastAPI, python-docx, pandas, SQLAlchemy
- **Frontend:** React 19, TypeScript, Material UI, TipTap editor
- **Deployment:** Docker / Docker Compose

## Documentation

Full documentation is available at the [DocForge docs site](docs/) or by running:

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and the PR process.

## License

DocForge is released under the [MIT License](LICENSE).
