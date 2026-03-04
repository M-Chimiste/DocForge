"""Format conversion utilities for DocForge."""

from __future__ import annotations

from docx.text.run import Run


def clear_red_color(run: Run) -> None:
    """Remove red font color from a run, setting it to automatic/black."""
    run.font.color.rgb = None
