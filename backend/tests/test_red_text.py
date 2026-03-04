"""Tests for red text detection and classification."""

from lxml import etree

from core.models import MarkerType
from utils.red_text import classify_marker, is_red_run


def _make_run_element(color_val: str | None = None) -> etree._Element:
    """Create a minimal w:r XML element with optional color."""
    nsmap = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    r = etree.SubElement(
        etree.Element("root", nsmap=nsmap),
        "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r",
    )
    if color_val is not None:
        rpr = etree.SubElement(
            r, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr"
        )
        color = etree.SubElement(
            rpr, "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color"
        )
        color.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val", color_val)
    return r


class TestIsRedRun:
    def test_red_run_detected(self):
        run = _make_run_element("FF0000")
        assert is_red_run(run) is True

    def test_red_run_lowercase(self):
        run = _make_run_element("ff0000")
        assert is_red_run(run) is True

    def test_non_red_color(self):
        run = _make_run_element("0000FF")
        assert is_red_run(run) is False

    def test_no_color_property(self):
        run = _make_run_element(None)
        assert is_red_run(run) is False

    def test_no_rpr(self):
        nsmap = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        r = etree.SubElement(
            etree.Element("root", nsmap=nsmap),
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r",
        )
        assert is_red_run(r) is False

    def test_near_red_not_detected(self):
        """Slightly off-red like FF0001 should NOT be detected."""
        run = _make_run_element("FF0001")
        assert is_red_run(run) is False


class TestClassifyMarker:
    def test_sample_data_in_table(self):
        result = classify_marker("Some data value", in_table_data_row=True)
        assert result == MarkerType.SAMPLE_DATA

    def test_short_label_is_placeholder(self):
        assert classify_marker("Project Name") == MarkerType.VARIABLE_PLACEHOLDER
        assert classify_marker("Author") == MarkerType.VARIABLE_PLACEHOLDER
        assert classify_marker("Report Date") == MarkerType.VARIABLE_PLACEHOLDER

    def test_long_text_is_llm_prompt(self):
        text = "Summarize the key findings from the quarterly metrics data"
        assert classify_marker(text) == MarkerType.LLM_PROMPT

    def test_four_words_is_llm_prompt(self):
        text = "The Project Name Here"
        assert classify_marker(text) == MarkerType.LLM_PROMPT

    def test_punctuation_makes_llm_prompt(self):
        assert classify_marker("Name.") == MarkerType.LLM_PROMPT
        assert classify_marker("Name, Title") == MarkerType.LLM_PROMPT

    def test_instruction_words_are_llm_prompt(self):
        assert classify_marker("Summarize Results") == MarkerType.LLM_PROMPT
        assert classify_marker("Describe Findings") == MarkerType.LLM_PROMPT

    def test_empty_text_is_llm_prompt(self):
        assert classify_marker("") == MarkerType.LLM_PROMPT
        assert classify_marker("   ") == MarkerType.LLM_PROMPT

    def test_table_data_row_overrides_label(self):
        """Even short label text is SAMPLE_DATA if in a table data row."""
        result = classify_marker("Name", in_table_data_row=True)
        assert result == MarkerType.SAMPLE_DATA
