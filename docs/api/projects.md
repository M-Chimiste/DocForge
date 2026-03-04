# Projects API

Projects are the top-level organizational unit in DocForge. Each project contains a template, data sources, mappings, and generation history.

## Create a Project

```
POST /api/v1/projects
```

**Request Body:**

```json
{
  "name": "Quarterly Report",
  "description": "Q1 2026 financial report"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Project name |
| `description` | string | No | Project description (default: `""`) |

**Response:** `200 OK`

```json
{
  "id": 1,
  "name": "Quarterly Report",
  "description": "Q1 2026 financial report",
  "templatePath": null,
  "createdAt": "2026-03-04T10:30:00",
  "updatedAt": "2026-03-04T10:30:00"
}
```

**curl Example:**

```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Quarterly Report", "description": "Q1 2026 financial report"}'
```

## List Projects

```
GET /api/v1/projects
```

Returns all projects ordered by most recently updated.

**Response:** `200 OK`

```json
[
  {
    "id": 1,
    "name": "Quarterly Report",
    "description": "Q1 2026 financial report",
    "templatePath": "/uploads/template.docx",
    "createdAt": "2026-03-04T10:30:00",
    "updatedAt": "2026-03-04T11:00:00"
  }
]
```

**curl Example:**

```bash
curl http://localhost:8000/api/v1/projects
```

## Get a Project

```
GET /api/v1/projects/{project_id}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `project_id` | integer | Project ID |

**Response:** `200 OK`

```json
{
  "id": 1,
  "name": "Quarterly Report",
  "description": "Q1 2026 financial report",
  "templatePath": "/uploads/template.docx",
  "createdAt": "2026-03-04T10:30:00",
  "updatedAt": "2026-03-04T11:00:00"
}
```

**Error:** `404 Not Found` if the project does not exist.

**curl Example:**

```bash
curl http://localhost:8000/api/v1/projects/1
```

## Update a Project

```
PUT /api/v1/projects/{project_id}
```

**Request Body:**

```json
{
  "name": "Updated Report Name",
  "description": "Updated description",
  "mappingConfig": {"marker_0": {"dataSource": "data.xlsx"}}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Updated project name |
| `description` | string | No | Updated description |
| `mappingConfig` | object | No | Mapping configuration to persist |

All fields are optional. Only provided fields are updated.

**Response:** `200 OK` -- Returns the updated project.

**curl Example:**

```bash
curl -X PUT http://localhost:8000/api/v1/projects/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Renamed Report"}'
```

## Delete a Project

```
DELETE /api/v1/projects/{project_id}
```

**Response:** `200 OK`

```json
{
  "ok": true
}
```

**Error:** `404 Not Found` if the project does not exist.

**curl Example:**

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/1
```

## Project Export

```
GET /api/v1/projects/{project_id}/export
```

Exports the entire project as a downloadable archive containing the template, data sources, and configuration.

**curl Example:**

```bash
curl -O http://localhost:8000/api/v1/projects/1/export
```

## Response Schema

### ProjectResponse

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Project ID |
| `name` | string | Project name |
| `description` | string | Project description |
| `templatePath` | string or null | Path to the uploaded template file |
| `createdAt` | string | ISO 8601 creation timestamp |
| `updatedAt` | string | ISO 8601 last update timestamp |
