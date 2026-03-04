"""Placeholder renderer: substitutes variable placeholder red text with mapped values."""

from __future__ import annotations

from docx import Document

from core.data_loader import DataStore
from core.models import MappingEntry, MarkerType, RenderResult, TemplateMarker
from renderers.base import BaseRenderer
from utils.docx_helpers import copy_run_format, find_adjacent_non_red_run
from utils.formatting import clear_red_color


class PlaceholderRenderer(BaseRenderer):
    def can_handle(self, marker: TemplateMarker) -> bool:
        return marker.marker_type == MarkerType.VARIABLE_PLACEHOLDER

    def render(
        self,
        marker: TemplateMarker,
        data: DataStore,
        document: Document,
        mapping: MappingEntry,
    ) -> RenderResult:
        # Resolve the mapped value
        value = self._resolve_value(data, mapping)
        if value is None:
            return RenderResult(
                marker_id=marker.id,
                success=False,
                error=f"Could not resolve value from {mapping.data_source}:{mapping.field}",
            )

        # Find the paragraph containing this marker
        if marker.paragraph_index < 0 or marker.paragraph_index >= len(document.paragraphs):
            return RenderResult(
                marker_id=marker.id,
                success=False,
                error=f"Paragraph index {marker.paragraph_index} out of range",
            )

        paragraph = document.paragraphs[marker.paragraph_index]
        runs = paragraph.runs

        if not marker.run_indices or max(marker.run_indices) >= len(runs):
            return RenderResult(
                marker_id=marker.id,
                success=False,
                error="Run indices out of range",
            )

        # Get formatting from adjacent non-red run
        format_source = find_adjacent_non_red_run(paragraph, marker.run_indices)

        # Replace: set value on first red run, clear subsequent ones
        for i, run_idx in enumerate(marker.run_indices):
            run = runs[run_idx]
            if i == 0:
                run.text = str(value)
            else:
                run.text = ""
            # Remove red color
            clear_red_color(run)
            # Copy formatting from adjacent run if available
            if format_source:
                copy_run_format(format_source, run)

        return RenderResult(marker_id=marker.id, success=True)

    def _resolve_value(self, data: DataStore, mapping: MappingEntry) -> str | None:
        """Get the value to substitute from the data store."""
        if mapping.path:
            # JSON path extraction
            source = data.get(mapping.data_source)
            if source and "raw" in source.metadata:
                try:
                    from extractors.json_extractor import _resolve_path

                    resolved = _resolve_path(source.metadata["raw"], mapping.path)
                    return str(resolved)
                except (KeyError, IndexError):
                    return None

        df = data.get_dataframe(mapping.data_source, sheet=mapping.sheet)
        if df is None:
            return None

        if mapping.field and mapping.field in df.columns:
            # Return first row value for the field
            return str(df.iloc[0][mapping.field])

        return None
