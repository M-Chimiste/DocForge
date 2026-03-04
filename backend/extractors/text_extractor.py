"""Plain text data extractor for section content injection."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig


class TextExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".txt", ".text", ".md", ".rst")

    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData:
        config = config or ExtractionConfig()
        text = file_path.read_text(encoding=config.text_encoding)
        result = ExtractedData(source_path=file_path, text_content=text)
        result.dataframes["default"] = pd.DataFrame({"content": [text]})
        result.metadata["char_count"] = len(text)
        result.metadata["line_count"] = text.count("\n") + 1
        return result
