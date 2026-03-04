"""Tests for the plugin discovery system."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
from docx import Document

from core.data_loader import DataStore
from core.models import MappingEntry, RenderResult, TemplateMarker
from core.plugin_loader import discover_plugin_info, discover_plugins
from extractors.base import BaseExtractor, ExtractedData, ExtractionConfig, ExtractorRegistry
from renderers.base import BaseRenderer, RendererRegistry
from transforms.base import BaseTransform, TransformRegistry

# --- Stub plugins for testing ---


class StubRenderer(BaseRenderer):
    def can_handle(self, marker: TemplateMarker) -> bool:
        return marker.text == "stub_marker"

    def render(
        self, marker: TemplateMarker, data: DataStore, document: Document, mapping: MappingEntry
    ) -> RenderResult:
        return RenderResult(marker_id=marker.id, success=True)


class StubExtractor(BaseExtractor):
    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix == ".stub"

    def extract(self, file_path: Path, config: ExtractionConfig | None = None) -> ExtractedData:
        return ExtractedData(source_path=file_path, dataframes={"default": pd.DataFrame()})


class StubTransform(BaseTransform):
    def can_handle(self, transform_type: str) -> bool:
        return transform_type == "stub_transform"

    def apply(self, df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
        return df


class BrokenPlugin:
    def __init__(self):
        raise RuntimeError("Plugin initialization failed")


# --- Tests ---


def _make_entry_point(name: str, cls: type, dist_name: str = "test-pkg") -> MagicMock:
    ep = MagicMock()
    ep.name = name
    ep.load.return_value = cls
    ep.dist = MagicMock()
    ep.dist.name = dist_name
    ep.dist.version = "0.1.0"
    return ep


class TestDiscoverPlugins:
    def test_empty_discovery(self):
        with patch("importlib.metadata.entry_points", return_value=[]):
            result = discover_plugins("docforge.renderers")
        assert result == []

    def test_loads_valid_renderer(self):
        ep = _make_entry_point("stub", StubRenderer)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            result = discover_plugins("docforge.renderers")
        assert len(result) == 1
        assert isinstance(result[0], StubRenderer)

    def test_loads_valid_extractor(self):
        ep = _make_entry_point("stub", StubExtractor)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            result = discover_plugins("docforge.extractors")
        assert len(result) == 1
        assert isinstance(result[0], StubExtractor)

    def test_loads_valid_transform(self):
        ep = _make_entry_point("stub", StubTransform)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            result = discover_plugins("docforge.transforms")
        assert len(result) == 1
        assert isinstance(result[0], StubTransform)

    def test_handles_broken_plugin(self, caplog):
        ep = _make_entry_point("broken", BrokenPlugin)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            result = discover_plugins("docforge.renderers")
        assert result == []
        assert "Failed to load plugin broken" in caplog.text

    def test_handles_entry_points_error(self):
        with patch("importlib.metadata.entry_points", side_effect=Exception("scan failed")):
            result = discover_plugins("docforge.renderers")
        assert result == []

    def test_multiple_plugins(self):
        ep1 = _make_entry_point("stub1", StubRenderer, "pkg1")
        ep2 = _make_entry_point("stub2", StubExtractor, "pkg2")
        with patch("importlib.metadata.entry_points", return_value=[ep1, ep2]):
            result = discover_plugins("docforge.renderers")
        assert len(result) == 2


class TestDiscoverPluginInfo:
    def test_returns_metadata(self):
        ep = _make_entry_point("stub", StubRenderer)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            info = discover_plugin_info()
        assert len(info) == 3 * 1  # 3 groups, each returns the same mock
        assert info[0].name == "stub"
        assert info[0].package == "test-pkg"
        assert info[0].version == "0.1.0"

    def test_empty_when_no_plugins(self):
        with patch("importlib.metadata.entry_points", return_value=[]):
            info = discover_plugin_info()
        assert info == []


class TestRegistryLoadPlugins:
    def test_renderer_registry_loads_plugins(self):
        registry = RendererRegistry()
        ep = _make_entry_point("stub", StubRenderer)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            registry.load_plugins()
        assert len(registry._renderers) == 1
        assert isinstance(registry._renderers[0], StubRenderer)

    def test_extractor_registry_loads_plugins(self):
        registry = ExtractorRegistry()
        ep = _make_entry_point("stub", StubExtractor)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            registry.load_plugins()
        assert len(registry._extractors) == 1
        assert isinstance(registry._extractors[0], StubExtractor)

    def test_transform_registry_loads_plugins(self):
        registry = TransformRegistry()
        ep = _make_entry_point("stub", StubTransform)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            registry.load_plugins()
        assert len(registry._transforms) == 1
        assert isinstance(registry._transforms[0], StubTransform)

    def test_builtins_take_priority_over_plugins(self):
        """Built-in renderers registered first should be found before plugins."""
        registry = RendererRegistry()

        # Register a built-in that handles everything
        builtin = MagicMock(spec=BaseRenderer)
        builtin.can_handle.return_value = True
        registry.register(builtin)

        # Load a plugin
        ep = _make_entry_point("stub", StubRenderer)
        with patch("importlib.metadata.entry_points", return_value=[ep]):
            registry.load_plugins()

        # Built-in should be found first
        marker = MagicMock(spec=TemplateMarker)
        marker.text = "stub_marker"
        found = registry.get_renderer(marker)
        assert found is builtin
