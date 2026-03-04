"""Tests for data extractors."""

from pathlib import Path

import pytest

from extractors.base import ExtractionConfig
from extractors.csv_extractor import CsvExtractor
from extractors.excel_extractor import ExcelExtractor
from extractors.json_extractor import JsonExtractor

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "data"


@pytest.fixture
def metrics_xlsx():
    return FIXTURES_DIR / "metrics.xlsx"


@pytest.fixture
def project_status_csv():
    return FIXTURES_DIR / "project_status.csv"


@pytest.fixture
def config_json():
    return FIXTURES_DIR / "config.json"


class TestExcelExtractor:
    def test_can_handle_xlsx(self):
        ext = ExcelExtractor()
        assert ext.can_handle(Path("test.xlsx")) is True
        assert ext.can_handle(Path("test.xls")) is True
        assert ext.can_handle(Path("test.csv")) is False

    def test_reads_all_sheets(self, metrics_xlsx):
        ext = ExcelExtractor()
        result = ext.extract(metrics_xlsx)
        assert "Revenue" in result.dataframes
        assert "KPIs" in result.dataframes
        assert len(result.dataframes) == 2

    def test_reads_specific_sheet(self, metrics_xlsx):
        ext = ExcelExtractor()
        config = ExtractionConfig(sheet_name="Revenue")
        result = ext.extract(metrics_xlsx, config)
        assert len(result.dataframes) == 1
        assert "Revenue" in result.dataframes
        df = result.dataframes["Revenue"]
        assert list(df.columns) == ["Quarter", "Revenue", "Growth"]
        assert len(df) == 4

    def test_dataframe_values(self, metrics_xlsx):
        ext = ExcelExtractor()
        config = ExtractionConfig(sheet_name="KPIs")
        result = ext.extract(metrics_xlsx, config)
        df = result.dataframes["KPIs"]
        assert df.iloc[0]["Metric"] == "Users"
        assert df.iloc[0]["Value"] == 5000


class TestCsvExtractor:
    def test_can_handle_csv(self):
        ext = CsvExtractor()
        assert ext.can_handle(Path("test.csv")) is True
        assert ext.can_handle(Path("test.tsv")) is True
        assert ext.can_handle(Path("test.xlsx")) is False

    def test_reads_csv(self, project_status_csv):
        ext = CsvExtractor()
        result = ext.extract(project_status_csv)
        df = result.dataframes["default"]
        assert list(df.columns) == ["Project", "Status", "Progress", "Lead"]
        assert len(df) == 4

    def test_csv_values(self, project_status_csv):
        ext = CsvExtractor()
        result = ext.extract(project_status_csv)
        df = result.dataframes["default"]
        assert df.iloc[0]["Project"] == "Alpha"
        assert df.iloc[0]["Progress"] == 75

    def test_metadata(self, project_status_csv):
        ext = CsvExtractor()
        result = ext.extract(project_status_csv)
        assert result.metadata["row_count"] == 4
        assert result.metadata["columns"] == ["Project", "Status", "Progress", "Lead"]


class TestJsonExtractor:
    def test_can_handle_json(self):
        ext = JsonExtractor()
        assert ext.can_handle(Path("test.json")) is True
        assert ext.can_handle(Path("test.csv")) is False

    def test_reads_json(self, config_json):
        ext = JsonExtractor()
        result = ext.extract(config_json)
        assert "default" in result.dataframes
        assert "raw" in result.metadata

    def test_json_path_extraction(self, config_json):
        ext = JsonExtractor()
        config = ExtractionConfig(json_path="project")
        result = ext.extract(config_json, config)
        df = result.dataframes["project"]
        assert "name" in df.columns
        assert df.iloc[0]["name"] == "DocForge Demo"

    def test_json_nested_path(self, config_json):
        ext = JsonExtractor()
        config = ExtractionConfig(json_path="settings")
        result = ext.extract(config_json, config)
        df = result.dataframes["settings"]
        assert df.iloc[0]["author"] == "Test Author"

    def test_json_invalid_path(self, config_json):
        ext = JsonExtractor()
        config = ExtractionConfig(json_path="nonexistent")
        with pytest.raises(KeyError):
            ext.extract(config_json, config)
