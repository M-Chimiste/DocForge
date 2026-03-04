"""Plugin discovery API endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from core.plugin_loader import discover_plugin_info

router = APIRouter(tags=["plugins"])


@router.get("/plugins")
async def list_plugins():
    """Return metadata for all discovered plugins."""
    plugins = discover_plugin_info()
    return [
        {
            "name": p.name,
            "group": p.group,
            "package": p.package,
            "version": p.version,
        }
        for p in plugins
    ]
