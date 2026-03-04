"""Tests for the template parser."""

from pathlib import Path

import pytest

from core.models import MarkerType
from core.template_parser import parse_template

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "templates"


@pytest.fixture
def simple_placeholder_docx():
    return FIXTURES_DIR / "simple_placeholder.docx"


@pytest.fixture
def simple_table_docx():
    return FIXTURES_DIR / "simple_table.docx"


@pytest.fixture
def mixed_markers_docx():
    return FIXTURES_DIR / "mixed_markers.docx"


@pytest.fixture
def table_with_sample_data_docx():
    return FIXTURES_DIR / "table_with_sample_data.docx"


class TestSectionDetection:
    def test_detects_heading(self, simple_placeholder_docx):
        analysis = parse_template(simple_placeholder_docx)
        assert len(analysis.sections) == 1
        assert analysis.sections[0].title == "Introduction"
        assert analysis.sections[0].level == 1

    def test_multiple_sections(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        assert len(analysis.sections) == 3
        titles = [s.title for s in analysis.sections]
        assert "Project Overview" in titles
        assert "Key Metrics" in titles
        assert "Executive Summary" in titles

    def test_section_ids_are_unique(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        ids = [s.id for s in analysis.sections]
        assert len(ids) == len(set(ids))


class TestRedTextDetection:
    def test_detects_placeholder(self, simple_placeholder_docx):
        analysis = parse_template(simple_placeholder_docx)
        placeholders = [
            m for m in analysis.markers if m.marker_type == MarkerType.VARIABLE_PLACEHOLDER
        ]
        assert len(placeholders) == 1
        assert placeholders[0].text == "Project Name"

    def test_marker_has_section_id(self, simple_placeholder_docx):
        analysis = parse_template(simple_placeholder_docx)
        marker = analysis.markers[0]
        assert marker.section_id is not None
        assert marker.section_id == analysis.sections[0].id

    def test_markers_attached_to_sections(self, simple_placeholder_docx):
        analysis = parse_template(simple_placeholder_docx)
        section = analysis.sections[0]
        assert len(section.markers) == 1
        assert section.markers[0].text == "Project Name"


class TestMixedMarkers:
    def test_placeholder_count(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        placeholders = [
            m for m in analysis.markers if m.marker_type == MarkerType.VARIABLE_PLACEHOLDER
        ]
        assert len(placeholders) == 2
        texts = {m.text for m in placeholders}
        assert "Author" in texts
        assert "Report Date" in texts

    def test_llm_prompt_detected(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        prompts = [m for m in analysis.markers if m.marker_type == MarkerType.LLM_PROMPT]
        assert len(prompts) == 1
        assert "executive summary" in prompts[0].text.lower()

    def test_llm_prompt_in_correct_section(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        prompts = [m for m in analysis.markers if m.marker_type == MarkerType.LLM_PROMPT]
        prompt = prompts[0]
        # Find the "Executive Summary" section
        exec_section = next(s for s in analysis.sections if s.title == "Executive Summary")
        assert prompt.section_id == exec_section.id


class TestTableDetection:
    def test_detects_skeleton_table(self, simple_table_docx):
        analysis = parse_template(simple_table_docx)
        assert len(analysis.tables) == 1
        table = analysis.tables[0]
        assert table.headers == ["Metric", "Value", "Target"]
        assert table.row_count == 0

    def test_table_in_mixed_doc(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        assert len(analysis.tables) == 1
        assert analysis.tables[0].headers == ["Quarter", "Revenue", "Growth"]

    def test_sample_data_markers(self, table_with_sample_data_docx):
        analysis = parse_template(table_with_sample_data_docx)
        assert len(analysis.tables) == 1
        table = analysis.tables[0]
        assert table.row_count == 2
        assert len(table.sample_data_markers) > 0
        # All should be SAMPLE_DATA type
        for m in table.sample_data_markers:
            assert m.marker_type == MarkerType.SAMPLE_DATA
            assert m.table_id == table.id

    def test_table_ids_unique(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        ids = [t.id for t in analysis.tables]
        assert len(ids) == len(set(ids))


class TestMarkerIds:
    def test_all_marker_ids_unique(self, mixed_markers_docx):
        analysis = parse_template(mixed_markers_docx)
        ids = [m.id for m in analysis.markers]
        assert len(ids) == len(set(ids))

    def test_marker_ids_start_with_marker(self, simple_placeholder_docx):
        analysis = parse_template(simple_placeholder_docx)
        for m in analysis.markers:
            assert m.id.startswith("marker-")
