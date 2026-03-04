"""Red text detection and classification for DocForge templates.

Red text (#FF0000) in Word templates serves as the marker system:
- Sample data in table rows
- Variable placeholders (short, label-like)
- LLM prompts (default for everything else)
"""

from __future__ import annotations

from docx.oxml.ns import qn
from lxml import etree

from core.models import MarkerType

RED_RGB = "FF0000"


def is_red_run(run_element: etree._Element) -> bool:
    """Check if a run element has exact #FF0000 color at the run level.

    Inspects w:rPr/w:color[@w:val] on the run element itself.
    Does not inherit from paragraph or style — must be explicit on the run.
    """
    rpr = run_element.find(qn("w:rPr"))
    if rpr is None:
        return False
    color = rpr.find(qn("w:color"))
    if color is None:
        return False
    val = color.get(qn("w:val"), "").upper()
    return val == RED_RGB


def classify_marker(text: str, *, in_table_data_row: bool = False) -> MarkerType:
    """Apply the classification rule chain for red text.

    Priority order:
    1. If inside a table data row → SAMPLE_DATA
    2. If short label-like text (1-3 words, no punctuation) → VARIABLE_PLACEHOLDER
    3. Default → LLM_PROMPT
    """
    if in_table_data_row:
        return MarkerType.SAMPLE_DATA

    stripped = text.strip()
    if not stripped:
        return MarkerType.LLM_PROMPT

    words = stripped.split()
    if 1 <= len(words) <= 3 and _is_label_like(stripped):
        return MarkerType.VARIABLE_PLACEHOLDER

    return MarkerType.LLM_PROMPT


def _is_label_like(text: str) -> bool:
    """Heuristic: short text without sentence-like punctuation."""
    if any(c in text for c in ".!?,;:()[]{}\"'"):
        return False
    # Reject if it looks like an instruction (contains verbs/action words)
    lower = text.lower()
    instruction_signals = [
        "summarize",
        "describe",
        "list",
        "provide",
        "write",
        "explain",
        "analyze",
    ]
    if any(signal in lower for signal in instruction_signals):
        return False
    return True
