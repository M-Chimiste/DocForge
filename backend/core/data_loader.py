"""Data loading and DataStore for managing extracted data sources."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from extractors.base import ExtractedData, ExtractionConfig, ExtractorRegistry
from extractors.csv_extractor import CsvExtractor
from extractors.docx_extractor import DocxContentExtractor
from extractors.excel_extractor import ExcelExtractor
from extractors.json_extractor import JsonExtractor
from extractors.pdf_extractor import PdfExtractor
from extractors.pptx_extractor import PptxExtractor
from extractors.text_extractor import TextExtractor
from extractors.yaml_extractor import YamlExtractor


def create_default_registry() -> ExtractorRegistry:
    registry = ExtractorRegistry()
    registry.register(ExcelExtractor())
    registry.register(CsvExtractor())
    registry.register(JsonExtractor())
    registry.register(TextExtractor())
    registry.register(YamlExtractor())
    registry.register(DocxContentExtractor())
    registry.register(PptxExtractor())
    registry.register(PdfExtractor())
    return registry


class DataStore:
    """Holds all loaded data sources, keyed by filename."""

    def __init__(self):
        self._sources: dict[str, ExtractedData] = {}

    def add(self, name: str, data: ExtractedData) -> None:
        self._sources[name] = data

    def get(self, name: str) -> ExtractedData | None:
        return self._sources.get(name)

    def get_dataframe(self, source_name: str, sheet: str | None = None) -> pd.DataFrame | None:
        source = self._sources.get(source_name)
        if source is None:
            return None
        if sheet and sheet in source.dataframes:
            return source.dataframes[sheet]
        if source.dataframes:
            return next(iter(source.dataframes.values()))
        return None

    def list_sources(self) -> list[str]:
        return list(self._sources.keys())

    def get_fields(self, source_name: str, sheet: str | None = None) -> list[str]:
        """Get column names for a data source."""
        df = self.get_dataframe(source_name, sheet)
        if df is not None:
            return list(df.columns)
        return []

    def get_text(self, source_name: str) -> str | None:
        """Get raw text content for an unstructured data source."""
        source = self._sources.get(source_name)
        if source and source.text_content:
            return source.text_content
        return None


def load_data_sources(
    file_paths: list[Path],
    configs: dict[str, ExtractionConfig] | None = None,
    registry: ExtractorRegistry | None = None,
) -> DataStore:
    registry = registry or create_default_registry()
    configs = configs or {}
    store = DataStore()
    for path in file_paths:
        extractor = registry.get_extractor(path)
        config = configs.get(path.name)
        data = extractor.extract(path, config)
        store.add(path.name, data)
    return store
