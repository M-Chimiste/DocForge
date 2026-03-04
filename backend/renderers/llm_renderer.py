"""LLMRenderer: assemble context, call LLM, inject response into document."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from docx import Document

from core.data_loader import DataStore
from core.llm_client import LLMClient
from core.llm_context import ContextAssembler
from core.models import (
    MappingEntry,
    MarkerType,
    RenderResult,
    TemplateAnalysis,
    TemplateMarker,
)
from renderers.base import BaseRenderer
from utils.docx_helpers import inject_text_at_marker

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a document writing assistant. Generate clear, professional text "
    "that directly addresses the instruction. Do not include meta-commentary "
    "about the task. Output only the text to be inserted into the document."
)


class LLMRenderer(BaseRenderer):
    """Renders LLM_PROMPT markers by calling an LLM with assembled context.

    When no LLM client is configured, can_handle() returns False, allowing
    the TextRenderer to handle these markers as a fallback.
    """

    def __init__(self) -> None:
        self._llm_client: LLMClient | None = None
        self._analysis: TemplateAnalysis | None = None
        self._mappings: list[MappingEntry] = []
        self._context_assembler = ContextAssembler()
        self._progress_callback: Callable[[dict[str, Any]], None] | None = None

    def configure(
        self,
        llm_client: LLMClient | None,
        analysis: TemplateAnalysis | None,
        mappings: list[MappingEntry] | None,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        """Late-bind dependencies before the render loop."""
        self._llm_client = llm_client
        self._analysis = analysis
        self._mappings = mappings or []
        self._progress_callback = progress_callback

    def can_handle(self, marker: TemplateMarker) -> bool:
        return (
            marker.marker_type == MarkerType.LLM_PROMPT
            and self._llm_client is not None
            and self._llm_client._config.is_configured
        )

    def render(
        self,
        marker: TemplateMarker,
        data: DataStore,
        document: Document,
        mapping: MappingEntry,
    ) -> RenderResult:
        if self._progress_callback:
            self._progress_callback(
                {
                    "stage": "rendering",
                    "marker_id": marker.id,
                    "marker_text": marker.text[:80],
                    "status": "llm_call_started",
                }
            )

        try:
            # 1. Assemble context
            resolved_context = self._context_assembler.assemble(
                marker, self._analysis, data, self._mappings
            )

            # 2. Build prompt
            user_prompt = self._build_prompt(marker.text, resolved_context.context_text)

            # 3. Call LLM
            response = self._llm_client.complete(user_prompt, system=SYSTEM_PROMPT)

            # 4. Inject response into document
            success = inject_text_at_marker(
                marker.paragraph_index, marker.run_indices, document, response.content
            )
            if not success:
                return RenderResult(
                    marker_id=marker.id,
                    success=False,
                    error=f"Paragraph index {marker.paragraph_index} out of range",
                )

            if self._progress_callback:
                self._progress_callback(
                    {
                        "stage": "rendering",
                        "marker_id": marker.id,
                        "status": "llm_call_completed",
                        "tokens": response.total_tokens,
                    }
                )

            return RenderResult(
                marker_id=marker.id,
                success=True,
                llm_usage={
                    "prompt_tokens": response.prompt_tokens,
                    "completion_tokens": response.completion_tokens,
                    "model": response.model,
                },
            )

        except Exception as e:
            logger.warning("LLM render failed for %s: %s", marker.id, e)
            if self._progress_callback:
                self._progress_callback(
                    {
                        "stage": "rendering",
                        "marker_id": marker.id,
                        "status": "llm_call_failed",
                        "error": str(e),
                    }
                )
            return RenderResult(
                marker_id=marker.id,
                success=False,
                error=f"LLM call failed: {e}",
            )

    def _build_prompt(self, instruction: str, context_text: str) -> str:
        parts: list[str] = []
        if context_text:
            parts.append("CONTEXT DATA:\n" + context_text)
        parts.append("INSTRUCTION:\n" + instruction)
        return "\n\n".join(parts)
