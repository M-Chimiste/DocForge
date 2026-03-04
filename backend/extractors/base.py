"""Base classes for data extractors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass
class ExtractionConfig:
    sheet_name: str | None = None
    named_range: str | None = None
    delimiter: str = ","
    encoding: str = "utf-8"
    json_path: str | None = None


@dataclass
class ExtractedData:
    source_path: Path
    dataframes: dict[str, pd.DataFrame] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseExtractor(ABC):
    @abstractmethod
    def can_handle(self, file_path: Path) -> bool: ...

    @abstractmethod
    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData: ...


class ExtractorRegistry:
    def __init__(self):
        self._extractors: list[BaseExtractor] = []

    def register(self, extractor: BaseExtractor) -> None:
        self._extractors.append(extractor)

    def get_extractor(self, file_path: Path) -> BaseExtractor:
        for ext in self._extractors:
            if ext.can_handle(file_path):
                return ext
        raise ValueError(f"No extractor found for {file_path.suffix}")
