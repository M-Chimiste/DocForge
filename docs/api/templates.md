# Templates API

The templates API handles uploading and analyzing `.docx` template files.

## Analyze a Template

```
POST /api/v1/templates/analyze
```

Upload a `.docx` file and receive a structural analysis of the template, including detected sections, markers (red text), and tables.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | The `.docx` template file |

**Response:** `200 OK`

```json
{
  "sections": [
    {
      "id": "section_0",
      "title": "Executive Summary",
      "level": 1,
      "paragraphIndex": 2,
      "markers": []
    },
    {
      "id": "section_1",
      "title": "Financial Results",
      "level": 1,
      "paragraphIndex": 8,
      "markers": []
    }
  ],
  "markers": [
    {
      "id": "marker_0",
      "text": "Company Name",
      "markerType": "variable_placeholder",
      "sectionId": "section_0",
      "paragraphIndex": 3,
      "runIndices": [0],
      "tableId": null,
      "rowIndex": null
    },
    {
      "id": "marker_1",
      "text": "Provide an executive summary of the quarterly results",
      "markerType": "llm_prompt",
      "sectionId": "section_0",
      "paragraphIndex": 5,
      "runIndices": [0, 1],
      "tableId": null,
      "rowIndex": null
    },
    {
      "id": "marker_2",
      "text": "Acme Corp\t$1.2M\t$0.8M",
      "markerType": "sample_data",
      "sectionId": "section_1",
      "paragraphIndex": 12,
      "runIndices": [0, 1, 2],
      "tableId": "table_0",
      "rowIndex": 1
    }
  ],
  "tables": [
    {
      "id": "table_0",
      "sectionId": "section_1",
      "paragraphIndex": 10,
      "headers": ["Company", "Revenue", "Expenses"],
      "rowCount": 3,
      "sampleDataMarkers": []
    }
  ]
}
```

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/templates/analyze \
  -F "file=@my_template.docx"
```

## CLI Analysis

You can also analyze templates from the command line:

```bash
docforge analyze --template my_template.docx
```

This outputs the analysis as JSON to stdout.

## Analysis Response Schema

### TemplateAnalysis

| Field | Type | Description |
|-------|------|-------------|
| `sections` | array of Section | Document sections detected from heading styles |
| `markers` | array of TemplateMarker | All red text markers found in the template |
| `tables` | array of SkeletonTable | Tables with structure information |

### Section

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique section identifier (e.g., `"section_0"`) |
| `title` | string | Section heading text |
| `level` | integer | Heading level (1, 2, or 3) |
| `paragraphIndex` | integer | Index of the heading paragraph in the document |
| `markers` | array | Markers contained within this section |

### TemplateMarker

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique marker identifier (e.g., `"marker_0"`) |
| `text` | string | The red text content |
| `markerType` | string | One of: `variable_placeholder`, `sample_data`, `llm_prompt` |
| `sectionId` | string or null | ID of the containing section |
| `paragraphIndex` | integer | Index of the paragraph containing this marker |
| `runIndices` | array of integer | Word run indices that make up this marker |
| `tableId` | string or null | ID of the containing table (for sample_data markers) |
| `rowIndex` | integer or null | Row index within the table |

### SkeletonTable

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique table identifier (e.g., `"table_0"`) |
| `sectionId` | string or null | ID of the containing section |
| `paragraphIndex` | integer | Index of the table's position in the document |
| `headers` | array of string | Column header text values |
| `rowCount` | integer | Number of rows including headers |
| `sampleDataMarkers` | array | Sample data markers found in the table |

## Marker Type Classification

Red text is classified using a rule chain:

1. **Sample Data** -- Red text inside a table data row (high confidence)
2. **Variable Placeholder** -- 1-3 words with noun/label structure (medium confidence)
3. **LLM Prompt** -- Everything else (high confidence, this is the default)

Users can override classifications in the mapping panel. Overrides persist in the project database.
