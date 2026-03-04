"""Factory function for the default transform registry."""

from __future__ import annotations

from transforms.base import TransformRegistry
from transforms.computed import ComputedTransform
from transforms.filter import FilterTransform
from transforms.format import DateFormatTransform, NumberFormatTransform
from transforms.rename import RenameTransform
from transforms.sort import SortTransform


def create_default_transform_registry() -> TransformRegistry:
    registry = TransformRegistry()
    registry.register(RenameTransform())
    registry.register(FilterTransform())
    registry.register(SortTransform())
    registry.register(DateFormatTransform())
    registry.register(NumberFormatTransform())
    registry.register(ComputedTransform())
    return registry
