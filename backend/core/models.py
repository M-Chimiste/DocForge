"""Domain models for DocForge template analysis and generation."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class MarkerType(str, Enum):
    VARIABLE_PLACEHOLDER = "variable_placeholder"
    SAMPLE_DATA = "sample_data"
    LLM_PROMPT = "llm_prompt"


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


class MappingEntry(BaseModel):
    marker_id: str
    data_source: str
    field: str | None = None
    sheet: str | None = None
    path: str | None = None


class RenderResult(BaseModel):
    marker_id: str
    success: bool
    error: str | None = None
