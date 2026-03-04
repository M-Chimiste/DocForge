# Custom Renderers

Renderers are responsible for transforming template markers into document content. This guide covers how to build a custom renderer plugin.

## Base Class Contract

All renderers must extend `BaseRenderer` from `renderers.base`:

```python
from abc import ABC, abstractmethod
from docx import Document
from core.data_loader import DataStore
from core.models import MappingEntry, RenderResult, TemplateMarker

class BaseRenderer(ABC):
    @abstractmethod
    def can_handle(self, marker: TemplateMarker) -> bool:
        """Return True if this renderer handles this marker type."""
        ...

    @abstractmethod
    def render(
        self,
        marker: TemplateMarker,
        data: DataStore,
        document: Document,
        mapping: MappingEntry,
    ) -> RenderResult:
        """Apply the rendering transformation to the document."""
        ...
```

### `can_handle(marker)`

Called by the `RendererRegistry` to determine if this renderer should handle a given marker. Return `True` if your renderer should process this marker.

**Parameters:**

- `marker` (`TemplateMarker`) -- The template marker to evaluate, containing:
    - `id` -- Unique marker identifier
    - `text` -- The red text content
    - `marker_type` -- One of `MarkerType.VARIABLE_PLACEHOLDER`, `MarkerType.SAMPLE_DATA`, `MarkerType.LLM_PROMPT`
    - `section_id` -- Containing section ID
    - `paragraph_index` -- Document paragraph index
    - `run_indices` -- Word run indices
    - `table_id` -- Containing table ID (if in a table)
    - `row_index` -- Table row index (if in a table)

### `render(marker, data, document, mapping)`

Called to perform the actual rendering. Modify the `document` in place and return a `RenderResult`.

**Parameters:**

- `marker` (`TemplateMarker`) -- The marker being rendered
- `data` (`DataStore`) -- Access to all loaded data sources
- `document` (`Document`) -- The python-docx Document object to modify
- `mapping` (`MappingEntry`) -- The mapping configuration for this marker, containing:
    - `marker_id` -- Marker ID
    - `data_source` -- Data source filename
    - `field` -- Field/column name
    - `sheet` -- Sheet name (Excel)
    - `path` -- JSON path
    - `transforms` -- Transform pipeline

**Return:** `RenderResult` with:

- `marker_id` -- The marker's ID
- `success` -- `True` if rendering succeeded
- `error` -- Error message if `success` is `False`
- `rendered_by` -- Name of the renderer (for reporting)

## Example: Markdown Renderer

The `docforge-markdown-renderer` example plugin handles LLM prompt markers that start with `[markdown]`. It parses basic Markdown (bold, italic, headings) and writes formatted runs into the document.

```python
from core.models import MarkerType, RenderResult, TemplateMarker
from renderers.base import BaseRenderer

class MarkdownRenderer(BaseRenderer):
    def can_handle(self, marker: TemplateMarker) -> bool:
        return (
            marker.marker_type == MarkerType.LLM_PROMPT
            and marker.text.strip().lower().startswith("[markdown]")
        )

    def render(self, marker, data, document, mapping):
        # Resolve content from the data store
        content = data.get_text(mapping.data_source)
        if content is None:
            return RenderResult(
                marker_id=marker.id,
                success=False,
                error=f"Could not resolve content from {mapping.data_source}",
            )

        # Locate and modify the target paragraph
        paragraph = document.paragraphs[marker.paragraph_index]

        # Clear existing red text
        for run in paragraph.runs:
            run.text = ""

        # Write new content with formatting
        for line in content.splitlines():
            run = paragraph.add_run(line)
            if line.startswith("# "):
                run.bold = True

        return RenderResult(
            marker_id=marker.id,
            success=True,
            rendered_by="markdown",
        )
```

## Project Structure

```
docforge-markdown-renderer/
  pyproject.toml
  docforge_markdown_renderer/
    __init__.py
    renderer.py              # MarkdownRenderer class
  tests/
    test_renderer.py
```

## Entry Point Declaration

In `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "docforge-markdown-renderer"
version = "0.1.0"
description = "DocForge plugin: renders markdown-prefixed LLM prompts."
requires-python = ">=3.12"
dependencies = ["docforge"]

[project.entry-points."docforge.renderers"]
markdown = "docforge_markdown_renderer.renderer:MarkdownRenderer"
```

The entry point key (`markdown`) becomes the plugin name. The value is the dotted path to your renderer class.

## Renderer Priority

Renderers are registered in the order they are discovered. The registry iterates through all renderers and uses the first one whose `can_handle()` returns `True`. Built-in renderers are registered before plugins, so your plugin renderer will only be invoked if no built-in renderer claims the marker first.

To override built-in behavior, make your `can_handle()` more specific so it matches before the built-in renderer's broader check.

## Testing

Test your renderer in isolation using pytest:

```python
from docx import Document
from core.data_loader import DataStore
from core.models import MappingEntry, MarkerType, TemplateMarker
from docforge_markdown_renderer.renderer import MarkdownRenderer

def test_can_handle_markdown_marker():
    renderer = MarkdownRenderer()
    marker = TemplateMarker(
        id="m1",
        text="[markdown] Some instruction",
        marker_type=MarkerType.LLM_PROMPT,
        paragraph_index=0,
        run_indices=[0],
    )
    assert renderer.can_handle(marker) is True

def test_cannot_handle_plain_prompt():
    renderer = MarkdownRenderer()
    marker = TemplateMarker(
        id="m1",
        text="Summarize the results",
        marker_type=MarkerType.LLM_PROMPT,
        paragraph_index=0,
        run_indices=[0],
    )
    assert renderer.can_handle(marker) is False
```

## Accessing the DataStore

The `DataStore` object provides these methods for retrieving data:

- `data.get_text(source_name)` -- Get text content from a data source
- `data.get_dataframe(source_name, sheet=None)` -- Get a pandas DataFrame
- `data.get(source_name)` -- Get the full `ExtractedData` object

Use these to resolve content based on the mapping configuration.
