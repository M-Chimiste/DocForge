"""JSON data extractor with dot-notation path support."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig


class JsonExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".json"

    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData:
        config = config or ExtractionConfig()

        with open(file_path, encoding=config.encoding) as f:
            data = json.load(f)

        result = ExtractedData(source_path=file_path)

        if config.json_path:
            resolved = _resolve_path(data, config.json_path)
            df = _to_dataframe(resolved)
            result.dataframes[config.json_path] = df
        else:
            df = _to_dataframe(data)
            result.dataframes["default"] = df

        result.metadata["raw"] = data
        return result


def _resolve_path(data: Any, path: str) -> Any:
    """Resolve a dot-notation path like 'results.metrics' into nested data."""
    keys = path.split(".")
    current = data
    for key in keys:
        if isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key '{key}' not found in path '{path}'")
            current = current[key]
        elif isinstance(current, list) and key.isdigit():
            current = current[int(key)]
        else:
            raise KeyError(f"Cannot resolve path segment '{key}' in path '{path}'")
    return current


def _to_dataframe(data: Any) -> pd.DataFrame:
    """Convert JSON data to a DataFrame."""
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        # Flat dict: single-row DataFrame
        # Check if values are all scalars
        if all(not isinstance(v, (dict, list)) for v in data.values()):
            return pd.DataFrame([data])
        # Nested: try to normalize
        return pd.json_normalize(data)
    else:
        return pd.DataFrame({"value": [data]})
