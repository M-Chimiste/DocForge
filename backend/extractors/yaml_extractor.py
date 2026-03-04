"""YAML data extractor for semi-structured data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig


class YamlExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".yaml", ".yml")

    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData:
        config = config or ExtractionConfig()

        with open(file_path, encoding=config.encoding) as f:
            data = yaml.safe_load(f)

        result = ExtractedData(source_path=file_path)
        result.metadata["raw"] = data

        if config.yaml_path:
            resolved = _resolve_path(data, config.yaml_path)
            result.dataframes[config.yaml_path] = _to_dataframe(resolved)
        else:
            result.dataframes["default"] = _to_dataframe(data)

        return result


def _resolve_path(data: Any, path: str) -> Any:
    """Resolve a dot-notation path into nested data."""
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
    """Convert YAML data to a DataFrame."""
    if isinstance(data, list):
        return pd.DataFrame(data)
    elif isinstance(data, dict):
        if all(not isinstance(v, (dict, list)) for v in data.values()):
            return pd.DataFrame([data])
        return pd.json_normalize(data)
    else:
        return pd.DataFrame({"value": [data]})
