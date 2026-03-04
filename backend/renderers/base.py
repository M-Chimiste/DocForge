"""Base renderer classes and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod

from docx import Document

from core.data_loader import DataStore
from core.models import MappingEntry, RenderResult, TemplateMarker


class BaseRenderer(ABC):
    @abstractmethod
    def can_handle(self, marker: TemplateMarker) -> bool: ...

    @abstractmethod
    def render(
        self,
        marker: TemplateMarker,
        data: DataStore,
        document: Document,
        mapping: MappingEntry,
    ) -> RenderResult: ...


class RendererRegistry:
    def __init__(self):
        self._renderers: list[BaseRenderer] = []

    def register(self, renderer: BaseRenderer) -> None:
        self._renderers.append(renderer)

    def load_plugins(self) -> None:
        """Discover and register third-party renderer plugins via entry points."""
        from core.plugin_loader import ENTRY_POINT_GROUPS, discover_plugins

        for renderer in discover_plugins(ENTRY_POINT_GROUPS["renderers"]):
            self.register(renderer)

    def get_renderer(self, marker: TemplateMarker) -> BaseRenderer | None:
        for r in self._renderers:
            if r.can_handle(marker):
                return r
        return None
