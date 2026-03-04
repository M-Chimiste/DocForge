"""Generation engine: orchestrates the parse → ingest → render → output pipeline."""

from __future__ import annotations

from pathlib import Path

from docx import Document

from core.auto_resolver import AutoResolver
from core.conditional import evaluate_condition, remove_section_content
from core.data_loader import DataStore, load_data_sources
from core.models import (
    AutoResolutionReport,
    ConditionalConfig,
    GenerationReport,
    MappingEntry,
    RenderResult,
    TemplateAnalysis,
)
from core.template_parser import parse_template
from core.validators import validate_mappings, validate_output
from renderers.base import RendererRegistry
from renderers.placeholder_renderer import PlaceholderRenderer
from renderers.table_renderer import TableRenderer, render_table_direct
from renderers.text_renderer import TextRenderer
from transforms.base import TransformPipeline
from transforms.pipeline import create_default_transform_registry


class GenerationEngine:
    def __init__(self):
        self.renderer_registry = RendererRegistry()
        self.renderer_registry.register(TextRenderer())
        self.renderer_registry.register(PlaceholderRenderer())
        self.renderer_registry.register(TableRenderer())

        self.transform_registry = create_default_transform_registry()
        self.transform_pipeline = TransformPipeline(self.transform_registry)
        self.auto_resolver = AutoResolver()

    def analyze(self, template_path: Path) -> TemplateAnalysis:
        return parse_template(template_path)

    def auto_resolve(
        self, analysis: TemplateAnalysis, data_store: DataStore
    ) -> AutoResolutionReport:
        return self.auto_resolver.resolve(analysis, data_store)

    def generate(
        self,
        template_path: Path,
        data_paths: list[Path],
        mappings: list[MappingEntry],
        output_path: Path,
        conditionals: list[ConditionalConfig] | None = None,
    ) -> GenerationReport:
        # 1. Load a fresh copy of the template (we modify in-place)
        doc = Document(str(template_path))

        # 2. Parse for analysis (to get marker positions)
        analysis = parse_template(template_path)

        # 3. Ingest data
        data_store = load_data_sources(data_paths)

        # 4. Evaluate conditional sections and remove excluded sections
        removed_markers: set[str] = set()
        if conditionals:
            for cond in conditionals:
                should_include = evaluate_condition(cond, data_store)
                if not should_include:
                    removed = remove_section_content(doc, cond.section_id, analysis)
                    removed_markers.update(removed)

        # 5. Pre-generation validation
        pre_validation = validate_mappings(analysis, mappings, data_store)

        # 6. Build mapping lookups
        mapping_by_marker = {m.marker_id: m for m in mappings}
        mapping_by_table = {}
        for m in mappings:
            if m.marker_id.startswith("table-"):
                mapping_by_table[m.marker_id] = m

        # 7. Apply per-mapping transforms
        for mapping in mappings:
            if mapping.transforms:
                df = data_store.get_dataframe(mapping.data_source, sheet=mapping.sheet)
                if df is not None:
                    transform_dicts = [
                        {"type": t.type.value, "params": t.params} for t in mapping.transforms
                    ]
                    transformed = self.transform_pipeline.apply(df, transform_dicts)
                    source = data_store.get(mapping.data_source)
                    if source:
                        sheet_key = mapping.sheet or next(iter(source.dataframes.keys()))
                        source.dataframes[sheet_key] = transformed

        # 8. Render markers
        results: list[RenderResult] = []
        rendered_tables: set[str] = set()

        for marker in analysis.markers:
            if marker.id in removed_markers:
                continue

            mapping = mapping_by_marker.get(marker.id)
            if not mapping:
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

            if marker.table_id and marker.table_id in rendered_tables:
                continue

            try:
                result = renderer.render(marker, data_store, doc, mapping)
                results.append(result)
                if marker.table_id:
                    rendered_tables.add(marker.table_id)
            except Exception as e:
                results.append(RenderResult(marker_id=marker.id, success=False, error=str(e)))

        # 9. Render skeleton tables that have no sample data markers but have mappings
        for table in analysis.tables:
            if table.id not in rendered_tables and table.id in mapping_by_table:
                mapping = mapping_by_table[table.id]
                try:
                    result = render_table_direct(table.id, data_store, doc, mapping)
                    results.append(result)
                except Exception as e:
                    results.append(RenderResult(marker_id=table.id, success=False, error=str(e)))

        # 10. Post-generation validation
        post_validation = validate_output(doc)

        # 11. Save output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))

        # 12. Build generation report
        return GenerationReport(
            total_markers=len(analysis.markers),
            rendered=sum(1 for r in results if r.success),
            skipped=sum(1 for r in results if not r.success),
            warnings=[v for v in pre_validation + post_validation if v.level == "warning"],
            errors=[v for v in pre_validation + post_validation if v.level == "error"],
            results=results,
        )
