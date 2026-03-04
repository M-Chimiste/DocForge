# Custom Extractors

Extractors handle parsing data from file formats into DocForge's internal data structures. This guide covers how to build a custom extractor plugin.

## Base Class Contract

All extractors must extend `BaseExtractor` from `extractors.base`:

```python
from abc import ABC, abstractmethod
from pathlib import Path
from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig

class BaseExtractor(ABC):
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Return True if this extractor can handle the given file."""
        ...

    @abstractmethod
    def extract(
        self, file_path: Path, config: ExtractionConfig | None = None
    ) -> ExtractedData:
        """Extract data from the file and return an ExtractedData object."""
        ...
```

### `can_handle(file_path)`

Called by the `ExtractorRegistry` to determine if this extractor should handle a given file. Typically checks the file extension.

**Parameters:**

- `file_path` (`Path`) -- Path to the data file

**Return:** `True` if this extractor can handle the file.

### `extract(file_path, config)`

Called to parse the file and return structured data.

**Parameters:**

- `file_path` (`Path`) -- Path to the data file
- `config` (`ExtractionConfig | None`) -- Optional extraction configuration with fields:
    - `sheet_name` -- Specific sheet to extract (Excel)
    - `named_range` -- Named range within a sheet
    - `delimiter` -- Column separator (CSV)
    - `encoding` -- File encoding
    - `json_path` -- JSONPath expression
    - `yaml_path` -- YAML path expression
    - `slide_range` -- Slide range (PowerPoint)
    - `include_notes` -- Include speaker notes
    - `include_headers` -- First row is headers
    - `text_encoding` -- Text file encoding

**Return:** `ExtractedData` with:

- `source_path` -- Path to the original file
- `dataframes` -- Dict mapping sheet/table names to pandas DataFrames
- `metadata` -- Dict of extraction metadata (row counts, etc.)
- `text_content` -- Optional raw text content (for unstructured sources)

## Example: XML Extractor

The `docforge-xml-extractor` example plugin extracts tabular data from XML files by flattening repeated child elements into a DataFrame.

```python
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import pandas as pd

from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig


class XmlExtractor(BaseExtractor):
    """Extract tabular data from XML files."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".xml"

    def extract(
        self, file_path: Path, config: ExtractionConfig | None = None
    ) -> ExtractedData:
        tree = ET.parse(file_path)
        root = tree.getroot()

        rows = self._flatten(root)
        df = pd.DataFrame(rows) if rows else pd.DataFrame()

        # Use the root tag as the sheet/table name
        sheet_name = root.tag

        return ExtractedData(
            source_path=file_path,
            dataframes={sheet_name: df},
            metadata={"root_tag": root.tag, "row_count": len(rows)},
        )

    @staticmethod
    def _flatten(root: ET.Element) -> list[dict[str, Any]]:
        """Flatten child elements into dicts.

        Each direct child of root becomes a row. Its XML attributes
        become columns, and each sub-element contributes a column.
        """
        rows = []
        for child in root:
            row: dict[str, Any] = {}
            # Attributes become columns
            for attr, value in child.attrib.items():
                row[attr] = value
            # Sub-element text becomes columns
            for sub in child:
                row[sub.tag] = (sub.text or "").strip()
            rows.append(row)
        return rows
```

This handles XML like:

```xml
<employees>
  <employee id="1" department="eng">
    <name>Alice</name>
    <title>Developer</title>
  </employee>
  <employee id="2" department="sales">
    <name>Bob</name>
    <title>Manager</title>
  </employee>
</employees>
```

Producing a DataFrame with columns `id`, `department`, `name`, `title`.

## Project Structure

```
docforge-xml-extractor/
  pyproject.toml
  docforge_xml_extractor/
    __init__.py
    extractor.py             # XmlExtractor class
  tests/
    test_extractor.py
```

## Entry Point Declaration

In `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[project]
name = "docforge-xml-extractor"
version = "0.1.0"
description = "DocForge plugin: extracts data from XML files into DataFrames."
requires-python = ">=3.12"
dependencies = ["docforge"]

[project.entry-points."docforge.extractors"]
xml = "docforge_xml_extractor.extractor:XmlExtractor"
```

## The ExtractedData Model

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import pandas as pd

@dataclass
class ExtractedData:
    source_path: Path
    dataframes: dict[str, pd.DataFrame] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    text_content: str | None = None
```

### Guidelines

- **dataframes**: Map logical table names to DataFrames. For files with multiple tables (like Excel sheets), use the sheet name as the key. For single-table formats, use a descriptive name.
- **metadata**: Include useful information like row counts, column types, source format details. This is available to the UI for display.
- **text_content**: For unstructured sources (text, PDFs), include the raw text here. This is used by LLM context assembly and can be displayed in the data preview.

## Testing

```python
from pathlib import Path
from docforge_xml_extractor.extractor import XmlExtractor

def test_can_handle_xml():
    extractor = XmlExtractor()
    assert extractor.can_handle(Path("data.xml")) is True
    assert extractor.can_handle(Path("data.csv")) is False

def test_extract_employees(tmp_path):
    xml_content = """<employees>
      <employee id="1"><name>Alice</name></employee>
      <employee id="2"><name>Bob</name></employee>
    </employees>"""

    xml_file = tmp_path / "test.xml"
    xml_file.write_text(xml_content)

    extractor = XmlExtractor()
    result = extractor.extract(xml_file)

    assert "employees" in result.dataframes
    df = result.dataframes["employees"]
    assert len(df) == 2
    assert list(df.columns) == ["id", "name"]
```
