"""TextRenderer: inject multi-paragraph text content into designated sections."""

from __future__ import annotations

from docx import Document

from core.data_loader import DataStore
from core.models import MappingEntry, MarkerType, RenderResult, TemplateMarker
from renderers.base import BaseRenderer
from utils.docx_helpers import inject_text_at_marker


class TextRenderer(BaseRenderer):
    """Handles LLM_PROMPT markers mapped to text data sources.

    When an LLM_PROMPT marker is mapped to a data source with text_content,
    the TextRenderer injects that text directly. This allows text file content
    to fill template sections without LLM processing.
    """

    def can_handle(self, marker: TemplateMarker) -> bool:
        return marker.marker_type == MarkerType.LLM_PROMPT

    def render(
        self,
        marker: TemplateMarker,
        data: DataStore,
        document: Document,
        mapping: MappingEntry,
    ) -> RenderResult:
        # Get text content from data source
        text = data.get_text(mapping.data_source)
        if text is None:
            # Try getting from DataFrame's "content" column
            df = data.get_dataframe(mapping.data_source, sheet=mapping.sheet)
            if df is not None and "content" in df.columns:
                text = str(df.iloc[0]["content"])
            else:
                return RenderResult(
                    marker_id=marker.id,
                    success=False,
                    error=f"No text content found in {mapping.data_source}",
                )

        success = inject_text_at_marker(marker.paragraph_index, marker.run_indices, document, text)
        if not success:
            return RenderResult(
                marker_id=marker.id,
                success=False,
                error=f"Paragraph index {marker.paragraph_index} out of range",
            )

        return RenderResult(marker_id=marker.id, success=True)
