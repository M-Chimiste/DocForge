# Data Sources API

Manage data source files within a project. Data sources are used to populate template markers during generation.

## Upload a Data Source

```
POST /api/v1/projects/{project_id}/data-sources
```

Upload a data file to the project. Files are stored in the project's data directory.

**Request:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | Yes | The data file (`.xlsx`, `.csv`, `.json`, `.txt`, etc.) |

**Response:** `200 OK`

```json
{
  "filename": "financial_data.xlsx",
  "path": "/uploads/1/data/financial_data.xlsx",
  "size": 15234
}
```

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/data-sources \
  -F "file=@financial_data.xlsx"
```

## List Data Sources

```
GET /api/v1/projects/{project_id}/data-sources
```

Returns all data source files uploaded to the project.

**Response:** `200 OK`

```json
[
  {
    "filename": "financial_data.xlsx",
    "path": "/uploads/1/data/financial_data.xlsx",
    "size": 15234
  },
  {
    "filename": "notes.txt",
    "path": "/uploads/1/data/notes.txt",
    "size": 2048
  }
]
```

**curl Example:**

```bash
curl http://localhost:8000/api/v1/projects/1/data-sources
```

## Preview a Data Source

```
GET /api/v1/projects/{project_id}/data-sources/{filename}/preview
```

Returns a paginated preview of extracted data from the file.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `project_id` | integer | Project ID |
| `filename` | string | Data source filename |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `page_size` | integer | 50 | Rows per page (1-500) |

**Response:** `200 OK`

```json
{
  "source": "financial_data.xlsx",
  "sheets": ["Sheet1", "Summary"],
  "preview": {
    "Sheet1": {
      "columns": ["Name", "Revenue", "Expenses", "Profit"],
      "rows": [
        ["Acme Corp", "1200000", "800000", "400000"],
        ["Beta Inc", "950000", "620000", "330000"]
      ],
      "totalRows": 150,
      "page": 1,
      "pageSize": 50,
      "totalPages": 3
    }
  },
  "textSnippet": null
}
```

For text-based data sources (`.txt`, `.pdf`), the `textSnippet` field contains the first 500 characters of extracted text.

**curl Example:**

```bash
curl "http://localhost:8000/api/v1/projects/1/data-sources/financial_data.xlsx/preview?page=1&page_size=10"
```

## LLM-Based Extraction

```
POST /api/v1/projects/{project_id}/data-sources/{filename}/llm-extract
```

Use an LLM to extract structured data from an unstructured data source (e.g., a PDF or text file).

**Request Body:**

```json
{
  "fields": [
    {
      "name": "company",
      "type": "string",
      "description": "Company name"
    },
    {
      "name": "revenue",
      "type": "number",
      "description": "Annual revenue in USD"
    },
    {
      "name": "year",
      "type": "string",
      "description": "Fiscal year"
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fields` | array | Yes | Schema defining the fields to extract |
| `fields[].name` | string | Yes | Field name |
| `fields[].type` | string | No | Data type (`"string"`, `"number"`, default: `"string"`) |
| `fields[].description` | string | No | Description to help the LLM understand the field |

**Response:** `200 OK`

```json
{
  "columns": ["company", "revenue", "year"],
  "rows": [
    {"company": "Acme Corp", "revenue": 1200000, "year": "2025"},
    {"company": "Beta Inc", "revenue": 950000, "year": "2025"}
  ],
  "validationErrors": [],
  "llmModel": "gpt-4o",
  "tokensUsed": 1250
}
```

!!! note "LLM Required"
    This endpoint requires an LLM to be configured for the project. See [LLM Configuration](../user-guide/llm-config.md).

**curl Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/projects/1/data-sources/report.pdf/llm-extract" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": [
      {"name": "company", "type": "string", "description": "Company name"},
      {"name": "revenue", "type": "number", "description": "Annual revenue"}
    ]
  }'
```

## Auto-Resolution

```
POST /api/v1/projects/{project_id}/auto-resolve
```

Automatically resolve mappings between template markers and uploaded data sources using fuzzy matching.

**Prerequisites:**

- A template must be uploaded to the project.
- At least one data source must be uploaded.

**Response:** `200 OK`

```json
{
  "matches": [
    {
      "markerId": "marker_0",
      "dataSource": "financial_data.xlsx",
      "field": "company_name",
      "sheet": "Sheet1",
      "path": null,
      "confidence": 0.92,
      "matchType": "exact",
      "reasoning": "Exact field name match: 'Company Name' -> 'company_name'"
    }
  ],
  "unresolved": ["marker_3", "marker_5"]
}
```

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/auto-resolve
```

## Response Schemas

### DataPreviewResponse

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | Filename of the data source |
| `sheets` | array of string | Sheet/table names found in the file |
| `preview` | object | Map of sheet name to paginated preview data |
| `textSnippet` | string or null | First 500 chars of text content (for text sources) |

### AutoResolutionResponse

| Field | Type | Description |
|-------|------|-------------|
| `matches` | array | Successfully resolved mappings |
| `matches[].markerId` | string | Template marker ID |
| `matches[].dataSource` | string | Matched data source filename |
| `matches[].field` | string or null | Matched field/column name |
| `matches[].confidence` | float | Match confidence (0.0-1.0) |
| `matches[].matchType` | string | Strategy used: `exact`, `fuzzy`, `structural`, `file_reference` |
| `matches[].reasoning` | string | Human-readable explanation |
| `unresolved` | array of string | Marker IDs that could not be resolved |
