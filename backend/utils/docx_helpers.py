"""Low-level python-docx and lxml utilities for DocForge."""

from __future__ import annotations

from docx.text.paragraph import Paragraph
from docx.text.run import Run


def get_heading_level(paragraph: Paragraph) -> int | None:
    """Return heading level (1-9) if paragraph uses a Heading style, else None."""
    style_name = paragraph.style.name if paragraph.style else ""
    if style_name.startswith("Heading "):
        try:
            return int(style_name.split()[-1])
        except ValueError:
            return None
    return None


def copy_run_format(source_run: Run, target_run: Run) -> None:
    """Copy font formatting from source to target run, excluding color.

    This is used when replacing red text with mapped values — the replacement
    should carry the surrounding formatting but NOT the red color.
    """
    sf = source_run.font
    tf = target_run.font
    tf.bold = sf.bold
    tf.italic = sf.italic
    tf.underline = sf.underline
    tf.size = sf.size
    tf.name = sf.name
    # Explicitly do NOT copy color — we want to remove the red


def find_adjacent_non_red_run(paragraph: Paragraph, red_run_indices: list[int]) -> Run | None:
    """Find the nearest non-red run adjacent to the red runs for format copying."""
    runs = paragraph.runs

    # Try run before the first red run
    if red_run_indices and red_run_indices[0] > 0:
        return runs[red_run_indices[0] - 1]

    # Try run after the last red run
    if red_run_indices and red_run_indices[-1] < len(runs) - 1:
        return runs[red_run_indices[-1] + 1]

    return None
