"""PDF text extractor via markitdown."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from markitdown import MarkItDown

from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig


class PdfExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"

    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData:
        config = config or ExtractionConfig()

        md = MarkItDown(enable_plugins=False)
        conversion = md.convert(str(file_path))
        full_text = conversion.text_content or ""

        result = ExtractedData(source_path=file_path, text_content=full_text)
        result.dataframes["default"] = pd.DataFrame({"content": [full_text]})
        result.metadata["format"] = "pdf"
        return result
