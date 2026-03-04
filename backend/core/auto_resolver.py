"""Auto-resolution engine: fuzzy-match markers to data source fields."""

from __future__ import annotations

from thefuzz import fuzz

from core.data_loader import DataStore
from core.models import (
    AutoResolutionMatch,
    AutoResolutionReport,
    MarkerType,
    TemplateAnalysis,
    TemplateMarker,
)


class AutoResolver:
    """Matches template markers against loaded data sources."""

    def resolve(self, analysis: TemplateAnalysis, data_store: DataStore) -> AutoResolutionReport:
        matches: list[AutoResolutionMatch] = []
        unresolved: list[str] = []

        for marker in analysis.markers:
            match = self._resolve_marker(marker, data_store, analysis)
            if match:
                matches.append(match)
            else:
                unresolved.append(marker.id)

        return AutoResolutionReport(matches=matches, unresolved=unresolved)

    def _resolve_marker(
        self, marker: TemplateMarker, data_store: DataStore, analysis: TemplateAnalysis
    ) -> AutoResolutionMatch | None:
        if marker.marker_type == MarkerType.VARIABLE_PLACEHOLDER:
            return self._resolve_variable(marker, data_store)
        elif marker.marker_type == MarkerType.SAMPLE_DATA:
            return self._resolve_sample_data(marker, data_store, analysis)
        elif marker.marker_type == MarkerType.LLM_PROMPT:
            return self._resolve_llm_prompt(marker, data_store)
        return None

    def _resolve_variable(
        self, marker: TemplateMarker, data_store: DataStore
    ) -> AutoResolutionMatch | None:
        best_match: AutoResolutionMatch | None = None
        best_confidence = 0.0
        marker_text = marker.text.strip().lower()

        for source_name in data_store.list_sources():
            source = data_store.get(source_name)
            if not source:
                continue

            for sheet_name, df in source.dataframes.items():
                for col in df.columns:
                    col_lower = col.lower()

                    # Exact match
                    if marker_text == col_lower:
                        return AutoResolutionMatch(
                            marker_id=marker.id,
                            data_source=source_name,
                            field=col,
                            sheet=sheet_name if sheet_name != "default" else None,
                            confidence=1.0,
                            match_type="exact",
                            reasoning=f"Exact match: '{marker.text}' == '{col}'",
                        )

                    # Fuzzy match
                    ratio = fuzz.token_sort_ratio(marker_text, col_lower) / 100.0
                    if ratio > best_confidence and ratio >= 0.5:
                        best_confidence = ratio
                        best_match = AutoResolutionMatch(
                            marker_id=marker.id,
                            data_source=source_name,
                            field=col,
                            sheet=sheet_name if sheet_name != "default" else None,
                            confidence=round(ratio, 2),
                            match_type="fuzzy",
                            reasoning=f"Fuzzy match: '{marker.text}' ~ '{col}' ({ratio:.2f})",
                        )

            # Check JSON/YAML raw metadata keys
            if "raw" in source.metadata and isinstance(source.metadata["raw"], dict):
                for key in _flatten_keys(source.metadata["raw"]):
                    key_lower = key.split(".")[-1].lower()
                    if marker_text == key_lower:
                        return AutoResolutionMatch(
                            marker_id=marker.id,
                            data_source=source_name,
                            path=key,
                            confidence=0.9,
                            match_type="exact",
                            reasoning=f"Exact match to metadata key: '{marker.text}' == '{key}'",
                        )

        return best_match

    def _resolve_sample_data(
        self,
        marker: TemplateMarker,
        data_store: DataStore,
        analysis: TemplateAnalysis,
    ) -> AutoResolutionMatch | None:
        if not marker.table_id:
            return None

        table = next((t for t in analysis.tables if t.id == marker.table_id), None)
        if not table:
            return None

        best_match = None
        best_confidence = 0.0

        for source_name in data_store.list_sources():
            source = data_store.get(source_name)
            if not source:
                continue

            for sheet_name, df in source.dataframes.items():
                header_set = {h.lower() for h in table.headers}
                col_set = {c.lower() for c in df.columns}

                if not header_set or not col_set:
                    continue

                overlap = len(header_set & col_set)
                total = max(len(header_set), len(col_set))
                raw_confidence = overlap / total if total > 0 else 0.0

                # Scale to 0.6-0.8 range
                if raw_confidence > 0.3:
                    confidence = 0.6 + (raw_confidence * 0.2)
                else:
                    confidence = raw_confidence

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = AutoResolutionMatch(
                        marker_id=marker.id,
                        data_source=source_name,
                        sheet=sheet_name if sheet_name != "default" else None,
                        confidence=round(min(confidence, 0.8), 2),
                        match_type="structural",
                        reasoning=(
                            f"Structural match: table headers {table.headers} overlap "
                            f"with columns {list(df.columns)} ({overlap}/{total} match)"
                        ),
                    )

        return best_match

    def _resolve_llm_prompt(
        self, marker: TemplateMarker, data_store: DataStore
    ) -> AutoResolutionMatch | None:
        text = marker.text.lower()

        for source_name in data_store.list_sources():
            name_lower = source_name.lower()
            stem_lower = source_name.rsplit(".", 1)[0].lower().replace("_", " ")

            if name_lower in text or stem_lower in text:
                return AutoResolutionMatch(
                    marker_id=marker.id,
                    data_source=source_name,
                    confidence=1.0,
                    match_type="file_reference",
                    reasoning=f"File reference detected: '{source_name}' found in prompt text",
                )

        return None


def _flatten_keys(d: dict, prefix: str = "") -> list[str]:
    """Recursively flatten a dict into dot-notation keys."""
    keys = []
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        keys.append(full_key)
        if isinstance(v, dict):
            keys.extend(_flatten_keys(v, full_key))
    return keys
