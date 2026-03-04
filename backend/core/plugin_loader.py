"""Plugin discovery via Python entry points."""

from __future__ import annotations

import importlib.metadata
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ENTRY_POINT_GROUPS = {
    "renderers": "docforge.renderers",
    "extractors": "docforge.extractors",
    "transforms": "docforge.transforms",
}


@dataclass
class PluginInfo:
    name: str
    group: str
    package: str
    version: str


def discover_plugins(group: str) -> list:
    """Load and instantiate all plugins for a given entry point group.

    Returns a list of plugin instances. Failed loads are logged as warnings
    but never crash the application (fail-forward).
    """
    instances = []
    try:
        eps = importlib.metadata.entry_points(group=group)
    except Exception:
        logger.warning("Failed to query entry points for group %s", group)
        return instances

    for ep in eps:
        try:
            cls = ep.load()
            instances.append(cls())
            dist_name = ep.dist.name if ep.dist else "unknown"
            logger.info("Loaded plugin %s from %s", ep.name, dist_name)
        except Exception as e:
            logger.warning("Failed to load plugin %s: %s", ep.name, e)

    return instances


def discover_plugin_info() -> list[PluginInfo]:
    """Return metadata for all discovered plugins without instantiation."""
    plugins: list[PluginInfo] = []
    for label, group in ENTRY_POINT_GROUPS.items():
        try:
            eps = importlib.metadata.entry_points(group=group)
        except Exception:
            continue
        for ep in eps:
            dist_name = ep.dist.name if ep.dist else "unknown"
            dist_version = ep.dist.version if ep.dist else "unknown"
            plugins.append(
                PluginInfo(
                    name=ep.name,
                    group=label,
                    package=dist_name,
                    version=dist_version,
                )
            )
    return plugins
