"""Pydantic models for the TipTap-compatible document editor.

These models map directly to TipTap's ProseMirror JSON schema,
with custom extensions for DocForge marker metadata.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class EditorMark(BaseModel):
    """A TipTap mark (inline formatting).

    Standard marks: bold, italic, underline, textStyle
    Custom marks: docforgeRendered
    """

    type: str
    attrs: dict[str, Any] | None = None


class EditorNode(BaseModel):
    """A TipTap node (block or inline).

    Standard types: doc, heading, paragraph, text, table, tableRow,
                    tableCell, tableHeader, hardBreak
    Custom types: docforgeUnresolved
    """

    type: str
    attrs: dict[str, Any] | None = None
    marks: list[EditorMark] | None = None
    content: list[EditorNode] | None = None
    text: str | None = None


class MarkerEditorMeta(BaseModel):
    """Per-marker metadata carried into the editor."""

    marker_id: str
    marker_type: str  # "variable_placeholder", "sample_data", "llm_prompt"
    original_text: str
    rendered_by: str  # "placeholder", "table", "llm", "text", "unresolved"
    confidence: float | None = None
    llm_model: str | None = None
    llm_prompt_tokens: int | None = None
    section_id: str | None = None
    mapping_snapshot: dict[str, Any] | None = None


class EditorDocumentMeta(BaseModel):
    """Metadata about the generated document for the editor."""

    generation_run_id: int
    project_id: int
    template_analysis: dict[str, Any] | None = None
    marker_metadata: dict[str, MarkerEditorMeta] = {}


class EditorDocument(BaseModel):
    """Complete editor payload: TipTap JSON node tree + DocForge metadata."""

    content: EditorNode
    meta: EditorDocumentMeta
