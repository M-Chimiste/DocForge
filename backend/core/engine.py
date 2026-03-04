"""Generation engine: orchestrates the parse → ingest → render → output pipeline."""

from __future__ import annotations

from pathlib import Path

from docx import Document

from core.data_loader import load_data_sources
from core.models import MappingEntry, RenderResult, TemplateAnalysis
from core.template_parser import parse_template
from renderers.base import RendererRegistry
from renderers.placeholder_renderer import PlaceholderRenderer
from renderers.table_renderer import TableRenderer, render_table_direct


class GenerationEngine:
    def __init__(self):
        self.renderer_registry = RendererRegistry()
        self.renderer_registry.register(PlaceholderRenderer())
        self.renderer_registry.register(TableRenderer())

    def analyze(self, template_path: Path) -> TemplateAnalysis:
        return parse_template(template_path)

    def generate(
        self,
        template_path: Path,
        data_paths: list[Path],
        mappings: list[MappingEntry],
        output_path: Path,
    ) -> list[RenderResult]:
        # 1. Load a fresh copy of the template (we modify in-place)
        doc = Document(str(template_path))

        # 2. Parse for analysis (to get marker positions)
        analysis = parse_template(template_path)

        # 3. Ingest data
        data_store = load_data_sources(data_paths)

        # 4. Build mapping lookups
        mapping_by_marker = {m.marker_id: m for m in mappings}
        mapping_by_table = {}
        for m in mappings:
            # If a mapping references a table_id directly, store it
            if m.marker_id.startswith("table-"):
                mapping_by_table[m.marker_id] = m

        # 5. Render markers (placeholders, sample data)
        results: list[RenderResult] = []
        rendered_tables: set[str] = set()

        for marker in analysis.markers:
            mapping = mapping_by_marker.get(marker.id)
            if not mapping:
                # For sample data markers, check if there's a table-level mapping
                if marker.table_id and marker.table_id in mapping_by_table:
                    mapping = mapping_by_table[marker.table_id]
                else:
                    results.append(
                        RenderResult(
                            marker_id=marker.id,
                            success=False,
                            error="No mapping provided",
                        )
                    )
                    continue

            renderer = self.renderer_registry.get_renderer(marker)
            if renderer is None:
                results.append(
                    RenderResult(
                        marker_id=marker.id,
                        success=False,
                        error=f"No renderer for marker type {marker.marker_type}",
                    )
                )
                continue

            # For table renderers, only render once per table
            if marker.table_id and marker.table_id in rendered_tables:
                continue

            try:
                result = renderer.render(marker, data_store, doc, mapping)
                results.append(result)
                if marker.table_id:
                    rendered_tables.add(marker.table_id)
            except Exception as e:
                results.append(RenderResult(marker_id=marker.id, success=False, error=str(e)))

        # 6. Render skeleton tables that have no sample data markers but have mappings
        for table in analysis.tables:
            if table.id not in rendered_tables and table.id in mapping_by_table:
                mapping = mapping_by_table[table.id]
                try:
                    result = render_table_direct(table.id, data_store, doc, mapping)
                    results.append(result)
                except Exception as e:
                    results.append(RenderResult(marker_id=table.id, success=False, error=str(e)))

        # 7. Save output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return results
