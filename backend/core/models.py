"""Domain models for DocForge template analysis and generation."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel


class MarkerType(str, Enum):
    VARIABLE_PLACEHOLDER = "variable_placeholder"
    SAMPLE_DATA = "sample_data"
    LLM_PROMPT = "llm_prompt"


class TransformType(str, Enum):
    RENAME = "rename"
    FILTER = "filter"
    SORT = "sort"
    FORMAT_DATE = "format_date"
    FORMAT_NUMBER = "format_number"
    COMPUTED = "computed"


class TemplateMarker(BaseModel):
    id: str
    text: str
    marker_type: MarkerType
    section_id: str | None = None
    paragraph_index: int
    run_indices: list[int]
    table_id: str | None = None
    row_index: int | None = None


class Section(BaseModel):
    id: str
    title: str
    level: int
    paragraph_index: int
    markers: list[TemplateMarker] = []


class SkeletonTable(BaseModel):
    id: str
    section_id: str | None = None
    paragraph_index: int
    headers: list[str]
    row_count: int
    sample_data_markers: list[TemplateMarker] = []


class TemplateAnalysis(BaseModel):
    sections: list[Section]
    markers: list[TemplateMarker]
    tables: list[SkeletonTable]


class TransformConfig(BaseModel):
    type: TransformType
    params: dict[str, Any] = {}


class MappingEntry(BaseModel):
    marker_id: str
    data_source: str
    field: str | None = None
    sheet: str | None = None
    path: str | None = None
    transforms: list[TransformConfig] = []


class ConditionalConfig(BaseModel):
    section_id: str
    condition_type: str  # "data_presence" or "explicit"
    data_source: str | None = None
    field: str | None = None
    operator: str | None = None  # "equals", "not_equals", "contains", "gt", "lt"
    value: str | None = None
    include: bool = True


class RenderResult(BaseModel):
    marker_id: str
    success: bool
    error: str | None = None


class AutoResolutionMatch(BaseModel):
    marker_id: str
    data_source: str
    field: str | None = None
    sheet: str | None = None
    path: str | None = None
    confidence: float
    match_type: str  # "exact", "fuzzy", "structural", "file_reference"
    reasoning: str


class AutoResolutionReport(BaseModel):
    matches: list[AutoResolutionMatch]
    unresolved: list[str]


class ValidationIssue(BaseModel):
    level: str  # "error", "warning", "info"
    marker_id: str | None = None
    message: str


class GenerationReport(BaseModel):
    total_markers: int
    rendered: int
    skipped: int
    warnings: list[ValidationIssue]
    errors: list[ValidationIssue]
    auto_resolution_report: AutoResolutionReport | None = None
    results: list[RenderResult]
