# Data Sources

DocForge supports multiple data file formats for populating templates. This guide covers supported formats, uploading, and extraction configuration.

## Supported Formats

| Format | Extension | Extractor | Notes |
|--------|-----------|-----------|-------|
| Excel | `.xlsx` | ExcelExtractor | Multiple sheets supported |
| CSV | `.csv` | CsvExtractor | Configurable delimiter and encoding |
| TSV | `.tsv` | CsvExtractor | Tab-delimited variant |
| JSON | `.json` | JsonExtractor | Nested structures supported via JSON path |
| Plain Text | `.txt` | TextExtractor | Used for unstructured content |
| Word | `.docx` | DocxExtractor | Extract text content from Word documents |
| PowerPoint | `.pptx` | PptxExtractor | Extract slide content and notes |
| PDF | `.pdf` | PdfExtractor | Text extraction via markitdown |
| YAML | `.yaml`, `.yml` | YamlExtractor | Structured data |

## Uploading Data Sources

### Via the Web UI

1. Open your project workspace.
2. Click **Upload Data** in the data sources panel.
3. Select one or more files.
4. Files are stored in the project's data directory on the server.

### Via the API

```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/data-sources \
  -F "file=@financial_data.xlsx"
```

### Listing Data Sources

```bash
curl http://localhost:8000/api/v1/projects/{project_id}/data-sources
```

Returns a list of uploaded files with their names, paths, and sizes:

```json
[
  {
    "filename": "financial_data.xlsx",
    "path": "/uploads/1/data/financial_data.xlsx",
    "size": 15234
  }
]
```

## Data Preview

Before mapping, you can preview the extracted data to verify it was parsed correctly:

```bash
curl "http://localhost:8000/api/v1/projects/{project_id}/data-sources/financial_data.xlsx/preview?page=1&page_size=50"
```

The preview endpoint returns paginated data with sheet names, column headers, and row values:

```json
{
  "source": "financial_data.xlsx",
  "sheets": ["Sheet1", "Summary"],
  "preview": {
    "Sheet1": {
      "columns": ["Name", "Revenue", "Expenses"],
      "rows": [["Acme Corp", "1200000", "800000"]],
      "totalRows": 150,
      "page": 1,
      "pageSize": 50,
      "totalPages": 3
    }
  },
  "textSnippet": null
}
```

## Extraction Configuration

Each extractor supports specific configuration options:

### Excel

- **sheet_name** -- Extract a specific sheet (default: all sheets)
- **named_range** -- Extract a named range within a sheet
- **include_headers** -- Whether the first row contains headers (default: `true`)

### CSV/TSV

- **delimiter** -- Column separator character (default: `,` for CSV, `\t` for TSV)
- **encoding** -- File encoding (default: `utf-8`)
- **include_headers** -- Whether the first row contains headers (default: `true`)

### JSON

- **json_path** -- JSONPath expression to locate the data array within nested structures

### YAML

- **yaml_path** -- Path expression to locate the target data within YAML structure

### PowerPoint

- **slide_range** -- Range of slides to extract (e.g., `"1-5"`)
- **include_notes** -- Whether to include speaker notes (default: `true`)

### Text

- **text_encoding** -- File encoding (default: `utf-8`)

## Data Store

Internally, DocForge loads all project data sources into a `DataStore` object. The data store provides:

- **Structured data** as pandas DataFrames, accessible by source name and optional sheet name
- **Unstructured text** content, accessible by source name
- **Metadata** about each source (row counts, column types, etc.)

The data store is passed through the entire generation pipeline and is available to all renderers during document generation.

## LLM-Based Extraction

For unstructured data sources that need to be converted into structured tables, DocForge can use an LLM to extract fields:

```bash
curl -X POST "http://localhost:8000/api/v1/projects/{project_id}/data-sources/report.pdf/llm-extract" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": [
      {"name": "company", "type": "string", "description": "Company name"},
      {"name": "revenue", "type": "number", "description": "Annual revenue"}
    ]
  }'
```

This requires an LLM to be configured for the project. See [LLM Configuration](llm-config.md) for setup.
