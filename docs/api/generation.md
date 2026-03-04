# Generation API

The generation API triggers document generation and provides access to generation history and outputs.

## Generate a Document

```
POST /api/v1/projects/{project_id}/generate
```

Run the generation pipeline synchronously. Returns when generation is complete.

**Request Body:**

```json
{
  "mappings": [
    {
      "markerId": "marker_0",
      "dataSource": "financial_data.xlsx",
      "field": "company_name",
      "sheet": "Sheet1",
      "path": null,
      "transforms": []
    },
    {
      "markerId": "marker_1",
      "dataSource": "financial_data.xlsx",
      "field": null,
      "sheet": "Financials",
      "transforms": [
        {"type": "sort", "params": {"column": "revenue", "ascending": false}}
      ]
    }
  ],
  "conditionals": [
    {
      "sectionId": "section_3",
      "conditionType": "data_presence",
      "dataSource": "optional_data.xlsx",
      "include": true
    }
  ]
}
```

### MappingEntryRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `markerId` | string | Yes | Template marker ID |
| `dataSource` | string | Yes | Data source filename |
| `field` | string | No | Specific field/column to extract |
| `sheet` | string | No | Sheet name (for Excel files) |
| `path` | string | No | JSON path (for JSON files) |
| `transforms` | array | No | Transform pipeline to apply |

### TransformConfigRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Transform type (e.g., `sort`, `filter`, `format_number`) |
| `params` | object | No | Transform-specific parameters |

### ConditionalConfigRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sectionId` | string | Yes | Section to conditionally include/exclude |
| `conditionType` | string | Yes | `"data_presence"` or `"explicit"` |
| `dataSource` | string | No | Data source to check |
| `field` | string | No | Field to evaluate (for explicit conditions) |
| `operator` | string | No | `equals`, `not_equals`, `contains`, `gt`, `lt` |
| `value` | string | No | Value to compare against |
| `include` | boolean | No | Include section when condition is true (default: `true`) |

**Response:** `200 OK`

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

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": [
      {"markerId": "marker_0", "dataSource": "data.xlsx", "field": "name", "sheet": "Sheet1"}
    ]
  }'
```

## Generate with Streaming (SSE)

```
POST /api/v1/projects/{project_id}/generate-stream
```

Same request body as the synchronous endpoint, but returns a Server-Sent Events stream with real-time progress updates.

**Event Types:**

### progress

Emitted during generation for each processing step:

```
event: progress
data: {"stage": "render", "marker_id": "marker_0", "status": "complete"}
```

### complete

Emitted once when generation finishes successfully:

```
event: complete
data: {"runId": 1, "downloadUrl": "/api/v1/projects/1/generations/1/download", "report": {...}}
```

**curl Example:**

```bash
curl -N -X POST http://localhost:8000/api/v1/projects/1/generate-stream \
  -H "Content-Type: application/json" \
  -d '{"mappings": [{"markerId": "marker_0", "dataSource": "data.xlsx", "field": "name"}]}'
```

## Validate Mappings

```
POST /api/v1/projects/{project_id}/validate
```

Validate mapping configuration before generation. Returns a list of issues without running the full pipeline.

**Request Body:** Same as the generate endpoint (mappings and optionally conditionals).

**Response:** `200 OK`

```json
[
  {
    "level": "error",
    "markerId": "marker_2",
    "message": "Field 'revenue_total' not found in data source 'data.xlsx'"
  },
  {
    "level": "warning",
    "markerId": null,
    "message": "Data source 'notes.txt' is uploaded but not mapped to any marker"
  }
]
```

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/projects/1/validate \
  -H "Content-Type: application/json" \
  -d '{"mappings": [{"markerId": "marker_0", "dataSource": "data.xlsx", "field": "name"}]}'
```

## List Generation Runs

```
GET /api/v1/projects/{project_id}/generations
```

Returns all generation runs for a project, ordered by most recent first.

**Response:** `200 OK`

```json
[
  {
    "id": 2,
    "projectId": 1,
    "status": "completed",
    "report": {"totalMarkers": 5, "rendered": 5, "skipped": 0},
    "createdAt": "2026-03-04T12:00:00"
  },
  {
    "id": 1,
    "projectId": 1,
    "status": "completed",
    "report": {"totalMarkers": 5, "rendered": 4, "skipped": 1},
    "createdAt": "2026-03-04T11:00:00"
  }
]
```

**curl Example:**

```bash
curl http://localhost:8000/api/v1/projects/1/generations
```

## Get a Generation Run

```
GET /api/v1/projects/{project_id}/generations/{run_id}
```

**Response:** `200 OK`

```json
{
  "id": 1,
  "projectId": 1,
  "status": "completed",
  "report": {
    "totalMarkers": 5,
    "rendered": 4,
    "skipped": 1,
    "warnings": [],
    "errors": []
  },
  "createdAt": "2026-03-04T11:00:00"
}
```

**curl Example:**

```bash
curl http://localhost:8000/api/v1/projects/1/generations/1
```

## Download Generated Document

```
GET /api/v1/projects/{project_id}/generations/{run_id}/download
```

Downloads the generated `.docx` file.

**Response:** `200 OK` with `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`

**curl Example:**

```bash
curl -O http://localhost:8000/api/v1/projects/1/generations/1/download
```

## Response Schemas

### GenerateResponse

| Field | Type | Description |
|-------|------|-------------|
| `runId` | integer | ID of the generation run |
| `downloadUrl` | string | URL to download the generated document |
| `report` | GenerationReportResponse | Generation results summary |

### GenerationReportResponse

| Field | Type | Description |
|-------|------|-------------|
| `totalMarkers` | integer | Total template markers processed |
| `rendered` | integer | Successfully rendered markers |
| `skipped` | integer | Skipped markers (errors or missing data) |
| `warnings` | array | Warning-level issues |
| `errors` | array | Error-level issues |

### ValidationIssueResponse

| Field | Type | Description |
|-------|------|-------------|
| `level` | string | `"error"`, `"warning"`, or `"info"` |
| `markerId` | string or null | Related marker ID (if applicable) |
| `message` | string | Human-readable description |

### GenerationRunResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Generation run ID |
| `projectId` | integer | Parent project ID |
| `status` | string | Run status (e.g., `"completed"`) |
| `report` | object or null | Generation report data |
| `createdAt` | string | ISO 8601 creation timestamp |
