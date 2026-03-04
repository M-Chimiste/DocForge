from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    description: str = ""


class ProjectUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str | None = None
    description: str | None = None
    mapping_config: dict | None = Field(default=None, alias="mappingConfig")


class ProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    id: int
    name: str
    description: str
    template_path: str | None = Field(default=None, serialization_alias="templatePath")
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")


class TransformConfigRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    type: str
    params: dict[str, Any] = {}


class MappingEntryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    marker_id: str = Field(alias="markerId")
    data_source: str = Field(alias="dataSource")
    field: str | None = Field(default=None)
    sheet: str | None = Field(default=None)
    path: str | None = Field(default=None)
    transforms: list[TransformConfigRequest] = []


class ConditionalConfigRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    section_id: str = Field(alias="sectionId")
    condition_type: str = Field(alias="conditionType")
    data_source: str | None = Field(default=None, alias="dataSource")
    field: str | None = None
    operator: str | None = None
    value: str | None = None
    include: bool = True


class GenerateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    mappings: list[MappingEntryRequest]
    conditionals: list[ConditionalConfigRequest] = []


class ValidationIssueResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    level: str
    marker_id: str | None = Field(default=None, serialization_alias="markerId")
    message: str


class GenerationReportResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    total_markers: int = Field(serialization_alias="totalMarkers")
    rendered: int
    skipped: int
    warnings: list[ValidationIssueResponse]
    errors: list[ValidationIssueResponse]


class GenerateResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    run_id: int = Field(serialization_alias="runId")
    download_url: str = Field(serialization_alias="downloadUrl")
    report: GenerationReportResponse


class AutoResolutionMatchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    marker_id: str = Field(serialization_alias="markerId")
    data_source: str = Field(serialization_alias="dataSource")
    field: str | None = None
    sheet: str | None = None
    path: str | None = None
    confidence: float
    match_type: str = Field(serialization_alias="matchType")
    reasoning: str


class AutoResolutionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    matches: list[AutoResolutionMatchResponse]
    unresolved: list[str]


class GenerationRunResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    id: int
    project_id: int = Field(serialization_alias="projectId")
    status: str
    report: dict | None = None
    created_at: str = Field(serialization_alias="createdAt")


class DataPreviewResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    source: str
    sheets: list[str]
    preview: dict
    text_snippet: str | None = Field(default=None, serialization_alias="textSnippet")


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = {}
