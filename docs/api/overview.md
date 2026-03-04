# API Overview

DocForge exposes a RESTful API built with FastAPI. All endpoints are prefixed with `/api/v1/`.

## Base URL

```
http://localhost:8000/api/v1
```

## Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Authentication

The current version of DocForge does not require authentication. All endpoints are open.

## Request Format

- JSON request bodies use **camelCase** keys (e.g., `markerId`, `dataSource`).
- File uploads use `multipart/form-data`.
- Query parameters use **snake_case** (e.g., `page_size`).

## Response Format

All responses return JSON with **camelCase** keys. Successful responses return the resource directly. Error responses follow a consistent structure:

```json
{
  "error": "error_code",
  "message": "Human-readable description of the error",
  "details": {}
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created (for POST that creates a resource) |
| 400 | Bad request (invalid input, missing prerequisites) |
| 404 | Resource not found |
| 422 | Validation error (Pydantic schema mismatch) |
| 500 | Internal server error |

## Endpoint Groups

| Group | Base Path | Description |
|-------|-----------|-------------|
| [Projects](projects.md) | `/api/v1/projects` | CRUD for projects |
| [Templates](templates.md) | `/api/v1/templates` | Template upload and analysis |
| [Data Sources](data-sources.md) | `/api/v1/projects/{id}/data-sources` | Upload and manage data files |
| [Generation](generation.md) | `/api/v1/projects/{id}/generate` | Document generation and history |
| [Editor](editor.md) | `/api/v1/generations/{id}` | Editor document, save, export |
| LLM Config | `/api/v1/llm` and `/api/v1/projects/{id}/llm-config` | LLM provider configuration |
| Plugins | `/api/v1/plugins` | List installed plugins |

## Common Patterns

### Pagination

Data preview endpoints support pagination via query parameters:

```
GET /api/v1/projects/1/data-sources/file.xlsx/preview?page=1&page_size=50
```

### Server-Sent Events (SSE)

The streaming generation endpoint uses SSE for real-time progress:

```
POST /api/v1/projects/1/generate-stream
```

Events are sent as `progress` and `complete` event types.

### File Downloads

File download endpoints return the file directly with the appropriate `Content-Type` header:

```
GET /api/v1/projects/1/generations/1/download
```

Returns: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
