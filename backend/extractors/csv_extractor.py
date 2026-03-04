"""CSV/TSV data extractor."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig


class CsvExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".csv", ".tsv")

    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData:
        config = config or ExtractionConfig()

        delimiter = config.delimiter
        if file_path.suffix.lower() == ".tsv":
            delimiter = "\t"

        df = pd.read_csv(file_path, delimiter=delimiter, encoding=config.encoding)

        result = ExtractedData(source_path=file_path)
        result.dataframes["default"] = df
        result.metadata["columns"] = list(df.columns)
        result.metadata["row_count"] = len(df)
        return result
