"""XML extractor plugin for DocForge.

Handles ``.xml`` files by flattening the first level of repeated child
elements into a :class:`pandas.DataFrame`.  Element attributes and child
text nodes become columns.

Example XML::

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

Produces a DataFrame with columns ``id``, ``department``, ``name``,
``title`` and two rows.
"""

from __future__ import annotations

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
        tree = ET.parse(file_path)  # noqa: S314 -- trusted local file
        root = tree.getroot()

        rows = self._flatten(root)
        df = pd.DataFrame(rows) if rows else pd.DataFrame()

        # Use the root tag as the sheet/table name
        sheet_name = self._strip_namespace(root.tag)

        return ExtractedData(
            source_path=file_path,
            dataframes={sheet_name: df},
            metadata={"root_tag": root.tag, "row_count": len(rows)},
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _flatten(root: ET.Element) -> list[dict[str, Any]]:
        """Flatten the first level of repeated child elements into dicts.

        Each direct child of *root* becomes a row.  Its XML attributes are
        included as columns, and each sub-element contributes a column
        whose name is the sub-element tag and whose value is the element
        text.
        """
        rows: list[dict[str, Any]] = []
        for child in root:
            row: dict[str, Any] = {}

            # Attributes become columns
            for attr, value in child.attrib.items():
                row[XmlExtractor._strip_namespace(attr)] = value

            # Sub-element text becomes columns
            for sub in child:
                tag = XmlExtractor._strip_namespace(sub.tag)
                row[tag] = (sub.text or "").strip()

            # If the element has direct text content and no sub-elements,
            # store it under a "text" column.
            if not list(child) and child.text and child.text.strip():
                row["text"] = child.text.strip()

            rows.append(row)
        return rows

    @staticmethod
    def _strip_namespace(tag: str) -> str:
        """Remove XML namespace prefix: ``{http://...}local`` -> ``local``."""
        if tag.startswith("{"):
            return tag.split("}", 1)[1]
        return tag
