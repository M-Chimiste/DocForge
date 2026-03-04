"""Tests for core.llm_context — ContextAssembler and broadening detection."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.data_loader import DataStore
from core.llm_context import ContextAssembler
from core.models import (
    ContextScope,
    MappingEntry,
    MarkerType,
    Section,
    TemplateAnalysis,
    TemplateMarker,
)
from extractors.base import ExtractedData


def _make_marker(
    marker_id: str,
    text: str,
    section_id: str | None = None,
    marker_type: MarkerType = MarkerType.LLM_PROMPT,
) -> TemplateMarker:
    return TemplateMarker(
        id=marker_id,
        text=text,
        marker_type=marker_type,
        section_id=section_id,
        paragraph_index=0,
        run_indices=[0],
    )


def _make_analysis(
    sections: list[Section] | None = None,
    markers: list[TemplateMarker] | None = None,
) -> TemplateAnalysis:
    return TemplateAnalysis(
        sections=sections or [],
        markers=markers or [],
        tables=[],
    )


def _make_data_store(sources: dict[str, ExtractedData]) -> DataStore:
    store = DataStore()
    for name, data in sources.items():
        store.add(name, data)
    return store


# ---------------------------------------------------------------------------
# Broadening Detection
# ---------------------------------------------------------------------------


class TestBroadeningDetection:
    def setup_method(self):
        self.assembler = ContextAssembler()

    def test_no_broadening_simple_prompt(self):
        scope, signals = self.assembler.detect_broadening(
            "Summarize the key findings from this section"
        )
        assert scope == ContextScope.SECTION
        assert signals == []

    def test_all_sections(self):
        scope, signals = self.assembler.detect_broadening("Provide an overview of all sections")
        assert scope == ContextScope.DOCUMENT
        assert "all sections" in signals

    def test_entire_document(self):
        scope, signals = self.assembler.detect_broadening("Summarize the entire document")
        assert scope == ContextScope.DOCUMENT
        assert "entire document" in signals

    def test_overall(self):
        scope, signals = self.assembler.detect_broadening("Write an overall summary of the project")
        assert scope == ContextScope.DOCUMENT
        assert "overall" in signals

    def test_executive_summary(self):
        scope, signals = self.assembler.detect_broadening(
            "Write an executive summary covering the project"
        )
        assert scope == ContextScope.DOCUMENT
        assert "executive summary" in signals

    def test_cross_section(self):
        scope, signals = self.assembler.detect_broadening("Analyze cross-section dependencies")
        assert scope == ContextScope.DOCUMENT
        assert "cross-section" in signals

    def test_document_wide(self):
        scope, signals = self.assembler.detect_broadening("Perform a document-wide analysis")
        assert scope == ContextScope.DOCUMENT
        assert "document-wide" in signals

    def test_full_report(self):
        scope, signals = self.assembler.detect_broadening(
            "Generate a full report based on the data"
        )
        assert scope == ContextScope.DOCUMENT
        assert "full report" in signals

    def test_covering_all(self):
        scope, signals = self.assembler.detect_broadening(
            "Write a summary covering all project milestones"
        )
        assert scope == ContextScope.DOCUMENT
        assert "covering all" in signals

    def test_multiple_signals(self):
        scope, signals = self.assembler.detect_broadening(
            "Write an executive summary covering all sections of the entire document"
        )
        assert scope == ContextScope.DOCUMENT
        assert len(signals) >= 2

    def test_case_insensitive(self):
        scope, signals = self.assembler.detect_broadening("Write an EXECUTIVE SUMMARY")
        assert scope == ContextScope.DOCUMENT
        assert "executive summary" in signals


# ---------------------------------------------------------------------------
# Section-Scoped Context Assembly
# ---------------------------------------------------------------------------


class TestSectionScopedContext:
    def setup_method(self):
        self.assembler = ContextAssembler()

    def test_section_scoped_includes_only_section_data(self):
        m1 = _make_marker("marker-0", "Summarize revenue", section_id="section-0")
        m2 = _make_marker("marker-1", "Summarize costs", section_id="section-1")
        s0 = Section(id="section-0", title="Revenue", level=1, paragraph_index=0, markers=[m1])
        s1 = Section(id="section-1", title="Costs", level=1, paragraph_index=5, markers=[m2])
        analysis = _make_analysis(sections=[s0, s1], markers=[m1, m2])

        df_revenue = pd.DataFrame({"quarter": ["Q1", "Q2"], "amount": [100, 200]})
        df_costs = pd.DataFrame({"quarter": ["Q1", "Q2"], "amount": [50, 80]})
        store = _make_data_store(
            {
                "revenue.csv": ExtractedData(
                    source_path=Path("revenue.csv"),
                    dataframes={"default": df_revenue},
                    metadata={},
                ),
                "costs.csv": ExtractedData(
                    source_path=Path("costs.csv"),
                    dataframes={"default": df_costs},
                    metadata={},
                ),
            }
        )

        mappings = [
            MappingEntry(marker_id="marker-0", data_source="revenue.csv"),
            MappingEntry(marker_id="marker-1", data_source="costs.csv"),
        ]

        result = self.assembler.assemble(m1, analysis, store, mappings)

        assert result.scope == ContextScope.SECTION
        assert "revenue.csv" in result.included_sources
        assert "costs.csv" not in result.included_sources
        assert "Revenue" in result.context_text

    def test_no_section_falls_back_to_marker_mapping(self):
        m1 = _make_marker("marker-0", "Summarize data", section_id=None)
        analysis = _make_analysis(markers=[m1])
        store = _make_data_store(
            {
                "data.csv": ExtractedData(
                    source_path=Path("data.csv"),
                    dataframes={"default": pd.DataFrame({"x": [1, 2]})},
                    metadata={},
                ),
            }
        )
        mappings = [MappingEntry(marker_id="marker-0", data_source="data.csv")]

        result = self.assembler.assemble(m1, analysis, store, mappings)

        assert result.scope == ContextScope.SECTION
        assert "data.csv" in result.included_sources


class TestDocumentScopedContext:
    def setup_method(self):
        self.assembler = ContextAssembler()

    def test_document_scope_includes_all_mappings(self):
        m1 = _make_marker("marker-0", "Write an executive summary", section_id="section-0")
        s0 = Section(id="section-0", title="Summary", level=1, paragraph_index=0, markers=[m1])
        analysis = _make_analysis(sections=[s0], markers=[m1])

        store = _make_data_store(
            {
                "revenue.csv": ExtractedData(
                    source_path=Path("revenue.csv"),
                    dataframes={"default": pd.DataFrame({"q": ["Q1"], "val": [100]})},
                    metadata={},
                ),
                "costs.csv": ExtractedData(
                    source_path=Path("costs.csv"),
                    dataframes={"default": pd.DataFrame({"q": ["Q1"], "val": [50]})},
                    metadata={},
                ),
            }
        )

        mappings = [
            MappingEntry(marker_id="marker-0", data_source="revenue.csv"),
            MappingEntry(marker_id="marker-1", data_source="costs.csv"),
        ]

        result = self.assembler.assemble(m1, analysis, store, mappings)

        assert result.scope == ContextScope.DOCUMENT
        assert "revenue.csv" in result.included_sources
        assert "costs.csv" in result.included_sources
        assert "Full Document" in result.context_text


class TestTextContent:
    def setup_method(self):
        self.assembler = ContextAssembler()

    def test_text_source_included_in_context(self):
        m1 = _make_marker("marker-0", "Summarize this text", section_id="section-0")
        s0 = Section(id="section-0", title="Summary", level=1, paragraph_index=0, markers=[m1])
        analysis = _make_analysis(sections=[s0], markers=[m1])

        store = _make_data_store(
            {
                "report.txt": ExtractedData(
                    source_path=Path("report.txt"),
                    dataframes={},
                    metadata={},
                    text_content="This is the report content for Q1.",
                ),
            }
        )
        mappings = [MappingEntry(marker_id="marker-0", data_source="report.txt")]

        result = self.assembler.assemble(m1, analysis, store, mappings)

        assert "report.txt" in result.included_sources
        assert "This is the report content" in result.context_text

    def test_long_text_truncated(self):
        long_text = "x" * 10000
        m1 = _make_marker("marker-0", "Summarize", section_id="section-0")
        s0 = Section(id="section-0", title="S", level=1, paragraph_index=0, markers=[m1])
        analysis = _make_analysis(sections=[s0], markers=[m1])

        store = _make_data_store(
            {
                "big.txt": ExtractedData(
                    source_path=Path("big.txt"),
                    dataframes={},
                    metadata={},
                    text_content=long_text,
                ),
            }
        )
        mappings = [MappingEntry(marker_id="marker-0", data_source="big.txt")]

        result = self.assembler.assemble(m1, analysis, store, mappings)

        # Context text should be truncated, not full 10000 chars
        assert len(result.context_text) < 5000


class TestScopeOverride:
    def setup_method(self):
        self.assembler = ContextAssembler()

    def test_override_to_document(self):
        m1 = _make_marker("marker-0", "Simple section summary", section_id="section-0")
        s0 = Section(id="section-0", title="S", level=1, paragraph_index=0, markers=[m1])
        analysis = _make_analysis(sections=[s0], markers=[m1])

        store = _make_data_store(
            {
                "a.csv": ExtractedData(
                    source_path=Path("a.csv"),
                    dataframes={"default": pd.DataFrame({"x": [1]})},
                    metadata={},
                ),
                "b.csv": ExtractedData(
                    source_path=Path("b.csv"),
                    dataframes={"default": pd.DataFrame({"y": [2]})},
                    metadata={},
                ),
            }
        )
        mappings = [
            MappingEntry(marker_id="marker-0", data_source="a.csv"),
            MappingEntry(marker_id="marker-1", data_source="b.csv"),
        ]

        # Without override: section scope
        result_section = self.assembler.assemble(m1, analysis, store, mappings)
        assert result_section.scope == ContextScope.SECTION

        # With override: document scope
        result_doc = self.assembler.assemble(
            m1, analysis, store, mappings, scope_override=ContextScope.DOCUMENT
        )
        assert result_doc.scope == ContextScope.DOCUMENT
        assert "b.csv" in result_doc.included_sources
