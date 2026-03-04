"""Tests for the XmlExtractor plugin."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pandas as pd
import pytest

from docforge_xml_extractor.extractor import XmlExtractor


@pytest.fixture
def tmp_xml(tmp_path: Path) -> Path:
    """Write a small XML file and return its path."""
    xml_content = textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
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
    """)
    p = tmp_path / "staff.xml"
    p.write_text(xml_content, encoding="utf-8")
    return p


@pytest.fixture
def flat_xml(tmp_path: Path) -> Path:
    """XML with simple text-only children."""
    xml_content = textwrap.dedent("""\
        <items>
          <item>Widget</item>
          <item>Gadget</item>
        </items>
    """)
    p = tmp_path / "items.xml"
    p.write_text(xml_content, encoding="utf-8")
    return p


class TestCanHandle:
    def test_xml_extension(self, tmp_path: Path):
        ext = XmlExtractor()
        assert ext.can_handle(tmp_path / "data.xml")
        assert ext.can_handle(tmp_path / "DATA.XML")

    def test_non_xml(self, tmp_path: Path):
        ext = XmlExtractor()
        assert not ext.can_handle(tmp_path / "data.json")
        assert not ext.can_handle(tmp_path / "data.csv")


class TestExtract:
    def test_basic_extraction(self, tmp_xml: Path):
        ext = XmlExtractor()
        result = ext.extract(tmp_xml)

        assert "employees" in result.dataframes
        df = result.dataframes["employees"]

        assert len(df) == 2
        assert list(df.columns) == ["id", "department", "name", "title"]
        assert df.iloc[0]["name"] == "Alice"
        assert df.iloc[1]["department"] == "sales"

    def test_metadata(self, tmp_xml: Path):
        ext = XmlExtractor()
        result = ext.extract(tmp_xml)

        assert result.metadata["row_count"] == 2
        assert result.metadata["root_tag"] == "employees"

    def test_flat_text_elements(self, flat_xml: Path):
        ext = XmlExtractor()
        result = ext.extract(flat_xml)

        df = result.dataframes["items"]
        assert len(df) == 2
        assert "text" in df.columns
        assert df.iloc[0]["text"] == "Widget"

    def test_empty_xml(self, tmp_path: Path):
        p = tmp_path / "empty.xml"
        p.write_text("<root/>", encoding="utf-8")
        ext = XmlExtractor()
        result = ext.extract(p)

        assert "root" in result.dataframes
        assert result.dataframes["root"].empty

    def test_source_path_preserved(self, tmp_xml: Path):
        ext = XmlExtractor()
        result = ext.extract(tmp_xml)
        assert result.source_path == tmp_xml
