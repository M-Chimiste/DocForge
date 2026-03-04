"""Excel (.xlsx, .xls) data extractor."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig


class ExcelExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".xlsx", ".xls")

    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData:
        config = config or ExtractionConfig()
        result = ExtractedData(source_path=file_path)

        if config.sheet_name:
            df = pd.read_excel(file_path, sheet_name=config.sheet_name, engine="openpyxl")
            result.dataframes[config.sheet_name] = df
        else:
            all_sheets = pd.read_excel(file_path, sheet_name=None, engine="openpyxl")
            result.dataframes = all_sheets

        result.metadata["sheet_names"] = list(result.dataframes.keys())
        return result
