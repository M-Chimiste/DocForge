"""Context assembly and broadening detection for LLM prompts."""

from __future__ import annotations

import re

from core.data_loader import DataStore
from core.models import (
    ContextScope,
    MappingEntry,
    ResolvedContext,
    TemplateAnalysis,
    TemplateMarker,
)

BROADENING_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\ball\s+sections?\b", re.IGNORECASE), "all sections"),
    (re.compile(r"\bentire\s+document\b", re.IGNORECASE), "entire document"),
    (re.compile(r"\bcovering\s+all\b", re.IGNORECASE), "covering all"),
    (re.compile(r"\boverall\b", re.IGNORECASE), "overall"),
    (re.compile(r"\bexecutive\s+summary\b", re.IGNORECASE), "executive summary"),
    (re.compile(r"\bcross[\s-]section\b", re.IGNORECASE), "cross-section"),
    (re.compile(r"\bdocument[\s-]wide\b", re.IGNORECASE), "document-wide"),
    (re.compile(r"\bfull\s+report\b", re.IGNORECASE), "full report"),
]

TEXT_TRUNCATE_LIMIT = 4000
DF_HEAD_ROWS = 50


class ContextAssembler:
    """Assembles LLM context from data sources, scoped by section or document."""

    def detect_broadening(self, prompt_text: str) -> tuple[ContextScope, list[str]]:
        """Scan prompt text for broadening signals.

        Returns the resolved scope and a list of matched signal labels.
        """
        signals: list[str] = []
        for pattern, label in BROADENING_PATTERNS:
            if pattern.search(prompt_text):
                signals.append(label)
        scope = ContextScope.DOCUMENT if signals else ContextScope.SECTION
        return scope, signals

    def assemble(
        self,
        marker: TemplateMarker,
        analysis: TemplateAnalysis,
        data_store: DataStore,
        mappings: list[MappingEntry],
        scope_override: ContextScope | None = None,
    ) -> ResolvedContext:
        """Assemble context for an LLM prompt marker."""
        scope, signals = self.detect_broadening(marker.text)
        if scope_override:
            scope = scope_override

        if scope == ContextScope.SECTION:
            context_text, sources = self._assemble_section_context(
                marker, analysis, data_store, mappings
            )
        else:
            context_text, sources = self._assemble_document_context(analysis, data_store, mappings)

        return ResolvedContext(
            scope=scope,
            broadening_signals=signals,
            included_sources=sources,
            context_text=context_text,
            section_id=marker.section_id,
        )

    def _assemble_section_context(
        self,
        marker: TemplateMarker,
        analysis: TemplateAnalysis,
        data_store: DataStore,
        mappings: list[MappingEntry],
    ) -> tuple[str, list[str]]:
        """Gather data mapped to the marker's section only."""
        section = next((s for s in analysis.sections if s.id == marker.section_id), None)
        if not section:
            # No section — fall back to the mapping for this marker only
            relevant = [m for m in mappings if m.marker_id == marker.id]
            return self._gather_data(relevant, data_store, "")
        section_marker_ids = {m.id for m in section.markers}
        relevant = [m for m in mappings if m.marker_id in section_marker_ids]
        return self._gather_data(relevant, data_store, section.title)

    def _assemble_document_context(
        self,
        analysis: TemplateAnalysis,
        data_store: DataStore,
        mappings: list[MappingEntry],
    ) -> tuple[str, list[str]]:
        """Gather all mapped data across the entire document."""
        return self._gather_data(mappings, data_store, "Full Document")

    def _gather_data(
        self,
        mappings: list[MappingEntry],
        data_store: DataStore,
        section_title: str,
    ) -> tuple[str, list[str]]:
        """Build context string from the given mappings."""
        parts: list[str] = []
        if section_title:
            parts.append(f"Section: {section_title}")
        sources_used: set[str] = set()

        # Deduplicate data sources
        seen_sources: set[str] = set()
        for mapping in mappings:
            source_key = (mapping.data_source, mapping.sheet)
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)

            source_name = mapping.data_source
            text = data_store.get_text(source_name)
            if text:
                truncated = text[:TEXT_TRUNCATE_LIMIT]
                parts.append(f"--- {source_name} ---\n{truncated}")
                sources_used.add(source_name)
            else:
                df = data_store.get_dataframe(source_name, sheet=mapping.sheet)
                if df is not None:
                    parts.append(f"--- {source_name} ---\n{df.head(DF_HEAD_ROWS).to_string()}")
                    sources_used.add(source_name)

        return "\n\n".join(parts), sorted(sources_used)
