"""Tests for the AutoResolver: fuzzy-match markers to data source fields."""

from pathlib import Path

import pandas as pd

from core.auto_resolver import AutoResolver
from core.data_loader import DataStore
from core.models import (
    AutoResolutionReport,
    MarkerType,
    SkeletonTable,
    TemplateAnalysis,
    TemplateMarker,
)
from extractors.base import ExtractedData


def _make_marker(
    marker_id: str,
    text: str,
    marker_type: MarkerType = MarkerType.VARIABLE_PLACEHOLDER,
    table_id: str | None = None,
    section_id: str | None = None,
) -> TemplateMarker:
    return TemplateMarker(
        id=marker_id,
        text=text,
        marker_type=marker_type,
        paragraph_index=0,
        run_indices=[0],
        table_id=table_id,
        section_id=section_id,
    )


def _make_analysis(
    markers: list[TemplateMarker],
    tables: list[SkeletonTable] | None = None,
) -> TemplateAnalysis:
    return TemplateAnalysis(
        sections=[],
        markers=markers,
        tables=tables or [],
    )


class TestExactFieldMatch:
    def test_exact_field_match(self):
        """CSV-like source with 'Author' column, marker text 'Author' -> exact match 1.0."""
        store = DataStore()
        df = pd.DataFrame({"Author": ["Alice"], "Title": ["My Book"]})
        store.add(
            "report.csv",
            ExtractedData(source_path=Path("report.csv"), dataframes={"default": df}),
        )

        marker = _make_marker("m1", "Author")
        analysis = _make_analysis([marker])

        resolver = AutoResolver()
        report = resolver.resolve(analysis, store)

        assert len(report.matches) == 1
        assert report.matches[0].marker_id == "m1"
        assert report.matches[0].confidence == 1.0
        assert report.matches[0].match_type == "exact"
        assert report.matches[0].data_source == "report.csv"
        assert report.matches[0].field == "Author"
        assert len(report.unresolved) == 0


class TestFuzzyFieldMatch:
    def test_fuzzy_field_match(self):
        """Marker 'Proj Name' against column 'Project Name' -> fuzzy match >= 0.5."""
        store = DataStore()
        df = pd.DataFrame({"Project Name": ["DocForge"], "Status": ["Active"]})
        store.add(
            "projects.csv",
            ExtractedData(source_path=Path("projects.csv"), dataframes={"default": df}),
        )

        marker = _make_marker("m1", "Proj Name")
        analysis = _make_analysis([marker])

        resolver = AutoResolver()
        report = resolver.resolve(analysis, store)

        assert len(report.matches) == 1
        match = report.matches[0]
        assert match.marker_id == "m1"
        assert match.confidence >= 0.5
        assert match.match_type == "fuzzy"
        assert match.field == "Project Name"
        assert len(report.unresolved) == 0


class TestJsonKeyMatch:
    def test_json_key_match(self):
        """Marker 'date' against JSON source with nested metadata key."""
        store = DataStore()
        raw_data = {"project": {"date": "2026"}}
        store.add(
            "config.json",
            ExtractedData(
                source_path=Path("config.json"),
                dataframes={},
                metadata={"raw": raw_data},
            ),
        )

        marker = _make_marker("m1", "date")
        analysis = _make_analysis([marker])

        resolver = AutoResolver()
        report = resolver.resolve(analysis, store)

        assert len(report.matches) == 1
        match = report.matches[0]
        assert match.marker_id == "m1"
        assert match.data_source == "config.json"
        assert match.path == "project.date"
        assert match.confidence == 0.9
        assert match.match_type == "exact"
        assert len(report.unresolved) == 0


class TestStructuralTableMatch:
    def test_structural_table_match(self):
        """SAMPLE_DATA marker with table headers matching CSV columns -> structural match."""
        store = DataStore()
        df = pd.DataFrame({"Project": ["A"], "Status": ["Active"], "Progress": ["50%"]})
        store.add(
            "data.csv",
            ExtractedData(source_path=Path("data.csv"), dataframes={"default": df}),
        )

        marker = _make_marker(
            "m1",
            "Sample Row",
            marker_type=MarkerType.SAMPLE_DATA,
            table_id="table1",
        )
        table = SkeletonTable(
            id="table1",
            section_id=None,
            paragraph_index=0,
            headers=["Project", "Status", "Progress"],
            row_count=2,
            sample_data_markers=[marker],
        )
        analysis = _make_analysis([marker], tables=[table])

        resolver = AutoResolver()
        report = resolver.resolve(analysis, store)

        assert len(report.matches) == 1
        match = report.matches[0]
        assert match.marker_id == "m1"
        assert match.match_type == "structural"
        assert match.data_source == "data.csv"
        assert match.confidence > 0
        assert len(report.unresolved) == 0


class TestFileReferenceDetection:
    def test_file_reference_detection(self):
        """LLM_PROMPT marker mentioning file name -> file_reference match."""
        store = DataStore()
        df = pd.DataFrame({"metric": [100]})
        store.add(
            "quarterly_metrics.xlsx",
            ExtractedData(
                source_path=Path("quarterly_metrics.xlsx"),
                dataframes={"default": df},
            ),
        )

        marker = _make_marker(
            "m1",
            "Analyze quarterly_metrics.xlsx data",
            marker_type=MarkerType.LLM_PROMPT,
        )
        analysis = _make_analysis([marker])

        resolver = AutoResolver()
        report = resolver.resolve(analysis, store)

        assert len(report.matches) == 1
        match = report.matches[0]
        assert match.marker_id == "m1"
        assert match.match_type == "file_reference"
        assert match.confidence == 1.0
        assert match.data_source == "quarterly_metrics.xlsx"
        assert len(report.unresolved) == 0


class TestNoMatch:
    def test_no_match(self):
        """Marker with completely unrelated text -> appears in unresolved."""
        store = DataStore()
        df = pd.DataFrame({"Revenue": [1000], "Expenses": [500]})
        store.add(
            "finance.csv",
            ExtractedData(source_path=Path("finance.csv"), dataframes={"default": df}),
        )

        marker = _make_marker("m1", "Completely Unrelated")
        analysis = _make_analysis([marker])

        resolver = AutoResolver()
        report = resolver.resolve(analysis, store)

        assert len(report.matches) == 0
        assert "m1" in report.unresolved


class TestFullResolutionReport:
    def test_full_resolution_report(self):
        """Multiple markers: some match, some don't -> report has both matches and unresolved."""
        store = DataStore()
        df = pd.DataFrame({"Author": ["Alice"], "Date": ["2026-01-01"]})
        store.add(
            "metadata.csv",
            ExtractedData(source_path=Path("metadata.csv"), dataframes={"default": df}),
        )

        m1 = _make_marker("m1", "Author")
        m2 = _make_marker("m2", "Date")
        m3 = _make_marker("m3", "Nonexistent Field")
        analysis = _make_analysis([m1, m2, m3])

        resolver = AutoResolver()
        report = resolver.resolve(analysis, store)

        assert isinstance(report, AutoResolutionReport)
        assert len(report.matches) == 2
        matched_ids = {m.marker_id for m in report.matches}
        assert "m1" in matched_ids
        assert "m2" in matched_ids
        assert "m3" in report.unresolved
