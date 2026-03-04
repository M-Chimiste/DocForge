# Generation

Document generation is the core pipeline that transforms a template with data and mappings into a finished `.docx` document.

## Generation Pipeline

DocForge processes documents through a five-stage pipeline:

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
  Render      --> Execute renderers (placeholders -> tables -> LLM -> conditionals)
     |
     v
  Validate    --> Check completeness, flag low-confidence items
     |
     v
Output (.docx) + Report (.json)
```

Each stage has a single responsibility, is independently testable, and the order is deterministic.

## Starting a Generation

### Via the Web UI

1. Ensure your project has a template and data sources uploaded.
2. Review and configure mappings in the Mapping Panel.
3. Click **Generate**.
4. A progress indicator shows each stage.
5. When complete, the result opens in the built-in editor.

### Via the API (Synchronous)

```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/generate \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": [
      {
        "markerId": "marker_0",
        "dataSource": "data.xlsx",
        "field": "company_name",
        "sheet": "Sheet1"
      },
      {
        "markerId": "marker_1",
        "dataSource": "data.xlsx",
        "field": null,
        "sheet": "Financials"
      }
    ],
    "conditionals": []
  }'
```

Response:

```json
{
  "runId": 1,
  "downloadUrl": "/api/v1/projects/1/generations/1/download",
  "report": {
    "totalMarkers": 5,
    "rendered": 4,
    "skipped": 1,
    "warnings": [
      {
        "level": "warning",
        "markerId": "marker_3",
        "message": "Low confidence auto-resolution (0.62)"
      }
    ],
    "errors": []
  }
}
```

### Via the API (Streaming with SSE)

For real-time progress updates, use the streaming endpoint. This returns Server-Sent Events with progress updates during generation:

```bash
curl -N -X POST http://localhost:8000/api/v1/projects/{project_id}/generate-stream \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": [
      {"markerId": "marker_0", "dataSource": "data.xlsx", "field": "name"}
    ]
  }'
```

The stream emits two event types:

**Progress events** during generation:

```
event: progress
data: {"stage": "render", "marker_id": "marker_0", "status": "complete"}
```

**Complete event** when finished:

```
event: complete
data: {"runId": 1, "downloadUrl": "/api/v1/projects/1/generations/1/download", "report": {...}}
```

## Renderers

The render stage uses a strategy pattern where different renderer implementations handle different marker types:

| Renderer | Marker Type | Description |
|----------|------------|-------------|
| PlaceholderRenderer | `variable_placeholder` | Simple value substitution |
| TableRenderer | `sample_data` | Populate tables from DataFrames |
| TextRenderer | `variable_placeholder` (multi-paragraph) | Inject text blocks |
| LLMRenderer | `llm_prompt` | Assemble context, call LLM, inject response |
| ConditionalRenderer | (conditionals) | Include/exclude sections |

Renderers are registered in a `RendererRegistry` and consulted in priority order. The first renderer whose `can_handle()` returns `True` for a marker is used. Custom renderers can be added via the [plugin system](../plugins/developing-renderers.md).

## Fail-Forward Error Handling

Individual rendering failures do not abort the entire generation. Instead:

1. The failure is recorded in the generation report.
2. The affected section keeps its original red text (or shows an error marker).
3. Generation continues with the remaining markers.

This ensures you always get output you can work with, even if some sections need manual attention.

### Error Categories

- **Fatal** -- Template parse failure, database corruption -- aborts with a clear error message.
- **Recoverable** -- Missing data source, LLM timeout, schema mismatch -- skipped, recorded in report, generation continues.
- **Warning** -- Low-confidence mapping, unused data source, empty optional section -- recorded in report, highlighted in editor.

## Generation History

Each generation run is recorded in the database with:

- The mapping configuration snapshot
- The template analysis snapshot
- The auto-resolution report
- The output file path
- The generation report with warnings and errors

### Listing Past Runs

```bash
curl http://localhost:8000/api/v1/projects/{project_id}/generations
```

### Downloading a Previous Output

```bash
curl -O http://localhost:8000/api/v1/projects/{project_id}/generations/{run_id}/download
```

## CLI Generation

DocForge can also generate documents from the command line:

```bash
docforge generate \
  --template quarterly_report.docx \
  --data financial_data.xlsx \
  --mapping '{"marker_0": {"dataSource": "financial_data.xlsx", "field": "name"}}' \
  --output output.docx
```
