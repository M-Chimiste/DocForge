"""Tests for data loader and DataStore."""

from pathlib import Path

from core.data_loader import DataStore, create_default_registry, load_data_sources
from extractors.base import ExtractedData

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "data"


class TestDataStore:
    def test_add_and_get(self):
        store = DataStore()
        data = ExtractedData(source_path=Path("test.csv"))
        store.add("test.csv", data)
        assert store.get("test.csv") is data
        assert store.get("nonexistent") is None

    def test_list_sources(self):
        store = DataStore()
        store.add("a.csv", ExtractedData(source_path=Path("a.csv")))
        store.add("b.xlsx", ExtractedData(source_path=Path("b.xlsx")))
        assert sorted(store.list_sources()) == ["a.csv", "b.xlsx"]


class TestDefaultRegistry:
    def test_registry_handles_xlsx(self):
        reg = create_default_registry()
        ext = reg.get_extractor(Path("test.xlsx"))
        assert ext is not None

    def test_registry_handles_csv(self):
        reg = create_default_registry()
        ext = reg.get_extractor(Path("test.csv"))
        assert ext is not None

    def test_registry_handles_json(self):
        reg = create_default_registry()
        ext = reg.get_extractor(Path("test.json"))
        assert ext is not None


class TestLoadDataSources:
    def test_loads_multiple_sources(self):
        paths = [
            FIXTURES_DIR / "metrics.xlsx",
            FIXTURES_DIR / "project_status.csv",
            FIXTURES_DIR / "config.json",
        ]
        store = load_data_sources(paths)
        assert len(store.list_sources()) == 3
        assert store.get("metrics.xlsx") is not None
        assert store.get("project_status.csv") is not None
        assert store.get("config.json") is not None

    def test_get_dataframe(self):
        paths = [FIXTURES_DIR / "project_status.csv"]
        store = load_data_sources(paths)
        df = store.get_dataframe("project_status.csv")
        assert df is not None
        assert len(df) == 4

    def test_get_dataframe_with_sheet(self):
        paths = [FIXTURES_DIR / "metrics.xlsx"]
        store = load_data_sources(paths)
        df = store.get_dataframe("metrics.xlsx", sheet="KPIs")
        assert df is not None
        assert "Metric" in df.columns

    def test_get_fields(self):
        paths = [FIXTURES_DIR / "project_status.csv"]
        store = load_data_sources(paths)
        fields = store.get_fields("project_status.csv")
        assert fields == ["Project", "Status", "Progress", "Lead"]
