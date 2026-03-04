"""Validation API endpoint."""

from pathlib import Path

from fastapi import APIRouter, Request

from api.errors import DocForgeError
from api.schemas import (
    GenerateRequest,
    ValidationIssueResponse,
)
from core.data_loader import load_data_sources
from core.engine import GenerationEngine
from core.models import MappingEntry
from core.validators import validate_mappings
from db.models import Project

router = APIRouter(tags=["validation"])


@router.post("/projects/{project_id}/validate")
async def validate_project(
    project_id: int,
    body: GenerateRequest,
    request: Request,
) -> list[ValidationIssueResponse]:
    settings = request.app.state.settings
    session_factory = request.app.state.db

    with session_factory() as session:
        project = session.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise DocForgeError(
                error="not_found",
                message=f"Project {project_id} not found",
                status_code=404,
            )
        if not project.template_path:
            raise DocForgeError(
                error="no_template",
                message="No template associated with this project",
                status_code=400,
            )
        template_path = Path(project.template_path)

    if not template_path.exists():
        raise DocForgeError(
            error="template_missing",
            message="Template file not found on disk",
            status_code=400,
        )

    # Load data
    project_data_dir = settings.upload_dir / str(project_id) / "data"
    data_paths = list(project_data_dir.iterdir()) if project_data_dir.exists() else []
    data_store = load_data_sources(data_paths)

    # Parse template
    engine = GenerationEngine()
    analysis = engine.analyze(template_path)

    # Convert mappings
    mappings = [
        MappingEntry(
            marker_id=m.marker_id,
            data_source=m.data_source,
            field=m.field,
            sheet=m.sheet,
            path=m.path,
        )
        for m in body.mappings
    ]

    issues = validate_mappings(analysis, mappings, data_store)

    return [
        ValidationIssueResponse(level=i.level, marker_id=i.marker_id, message=i.message)
        for i in issues
    ]
