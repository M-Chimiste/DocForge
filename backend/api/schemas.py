from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str
    description: str = ""


class ProjectResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    id: int
    name: str
    description: str
    template_path: str | None = Field(default=None, serialization_alias="templatePath")
    created_at: str = Field(serialization_alias="createdAt")
    updated_at: str = Field(serialization_alias="updatedAt")


class MappingEntryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    marker_id: str = Field(alias="markerId")
    data_source: str = Field(alias="dataSource")
    field: str | None = Field(default=None)
    sheet: str | None = Field(default=None)
    path: str | None = Field(default=None)


class GenerateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    mappings: list[MappingEntryRequest]


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = {}
