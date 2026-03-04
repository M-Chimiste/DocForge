# Code Conventions

This document describes the naming, style, and structural conventions used throughout the DocForge codebase.

## Naming Conventions

| Area | Convention | Examples |
|------|-----------|----------|
| Backend modules | `snake_case` | `template_parser.py`, `data_loader.py` |
| Backend functions | `snake_case` | `load_data_sources()`, `auto_resolve()` |
| Backend variables | `snake_case` | `marker_type`, `template_path` |
| Backend classes | `PascalCase` | `GenerationEngine`, `BaseRenderer` |
| Frontend components | `PascalCase` | `TemplateUpload`, `MappingPanel` |
| Frontend functions | `camelCase` | `handleSubmit()`, `fetchProjects()` |
| Frontend props | `camelCase` | `projectId`, `onUpload` |
| Database tables | `snake_case` | `generation_runs`, `projects` |
| Database columns | `snake_case` | `template_path`, `created_at` |
| API JSON keys | `camelCase` | `markerId`, `dataSource`, `templatePath` |
| API URLs | kebab-case paths | `/api/v1/data-sources`, `/api/v1/llm-config` |
| Error codes | `snake_case` | `template_not_found`, `llm_timeout` |

## API Conventions

### URL Structure

All API endpoints are prefixed with `/api/v1/`:

```
/api/v1/projects
/api/v1/projects/{project_id}
/api/v1/projects/{project_id}/data-sources
/api/v1/projects/{project_id}/generate
/api/v1/templates/analyze
```

### Request/Response Format

- Request bodies use **camelCase** JSON keys.
- Response bodies use **camelCase** JSON keys.
- Pydantic models use `snake_case` internally with `Field(alias="camelCase")` or `Field(serialization_alias="camelCase")` for API boundary translation.

```python
class ProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    id: int
    name: str
    template_path: str | None = Field(default=None, serialization_alias="templatePath")
    created_at: str = Field(serialization_alias="createdAt")
```

### Error Format

All API errors return a consistent structure:

```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "details": {}
}
```

Error codes are defined in `core/error_catalog.py` with messages and remediation hints.

## Python Style

### Type Annotations

Use modern Python type syntax (3.10+):

```python
# Good
def process(items: list[str], config: dict[str, Any] | None = None) -> bool: ...

# Avoid (old-style)
def process(items: List[str], config: Optional[Dict[str, Any]] = None) -> bool: ...
```

Use `from __future__ import annotations` for forward references.

### Imports

Ruff enforces import sorting (isort-compatible). Order:

1. Standard library
2. Third-party packages
3. Local imports

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, Request

from core.models import MappingEntry, TemplateMarker
from renderers.base import BaseRenderer
```

### Docstrings

Use descriptive docstrings for modules, classes, and public functions:

```python
"""Template parser: extracts structure and red text markers from .docx files."""

class TemplateParser:
    """Parse a .docx template and return a structured analysis.

    The parser detects sections (from heading styles), tables,
    and red text markers (exact #FF0000 at the run level).
    """

    def parse(self, path: Path) -> TemplateAnalysis:
        """Parse the template at *path* and return the analysis."""
        ...
```

### Line Length

Maximum line length is **100 characters** (configured in `pyproject.toml`).

### Abstract Base Classes

Plugin interfaces use ABC with abstract methods:

```python
from abc import ABC, abstractmethod

class BaseRenderer(ABC):
    @abstractmethod
    def can_handle(self, marker: TemplateMarker) -> bool: ...

    @abstractmethod
    def render(self, marker, data, document, mapping) -> RenderResult: ...
```

## Frontend Style

### Component Structure

React components use functional components with TypeScript:

```typescript
interface TemplateUploadProps {
  projectId: number;
  onUpload: (analysis: TemplateAnalysis) -> void;
}

export function TemplateUpload({ projectId, onUpload }: TemplateUploadProps) {
  // Component implementation
}
```

### API Client

The frontend API client uses typed Axios wrappers in `src/api/`:

```typescript
export async function createProject(data: ProjectCreate): Promise<ProjectResponse> {
  const response = await api.post('/projects', data);
  return response.data;
}
```

### Type Definitions

TypeScript interfaces mirror the API response schemas:

```typescript
interface ProjectResponse {
  id: number;
  name: string;
  description: string;
  templatePath: string | null;
  createdAt: string;
  updatedAt: string;
}
```

## Testing Conventions

### Backend Tests

- Test files are named `test_<module>.py`.
- Test functions are named `test_<behavior>`.
- Use pytest fixtures for common setup.
- Use programmatic `.docx` fixtures from `tests/fixtures/create_fixtures.py`.
- Mock LLM calls -- never hit real APIs in tests.

```python
def test_placeholder_renderer_substitutes_value(sample_document, data_store):
    renderer = PlaceholderRenderer()
    marker = TemplateMarker(
        id="m1",
        text="Company Name",
        marker_type=MarkerType.VARIABLE_PLACEHOLDER,
        paragraph_index=0,
        run_indices=[0],
    )
    mapping = MappingEntry(marker_id="m1", data_source="data.xlsx", field="name")
    result = renderer.render(marker, data_store, sample_document, mapping)
    assert result.success is True
```

### Frontend Tests

- ESLint for code quality and style enforcement.
- TypeScript compiler for type safety.

## Database Conventions

### SQLAlchemy Models

```python
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    template_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```

- Table names: plural `snake_case` (e.g., `projects`, `generation_runs`)
- Column names: `snake_case`
- Timestamps: `created_at`, `updated_at` with server defaults

## Error Handling Conventions

### API Layer

Use the error catalog for consistent error responses:

```python
from api.errors import catalog_error

raise catalog_error("project_not_found", status_code=404, project_id=project_id)
```

### Service Layer

Use fail-forward for recoverable errors:

```python
try:
    result = renderer.render(marker, data, doc, mapping)
except Exception as e:
    results.append(RenderResult(marker_id=marker.id, success=False, error=str(e)))
    continue  # Don't abort the pipeline
```

### Fatal Errors

Raise exceptions directly for unrecoverable situations:

```python
if not template_path.exists():
    raise catalog_error("template_not_found", path=str(template_path))
```
